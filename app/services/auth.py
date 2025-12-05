from typing import Optional, Any, Dict
from datetime import timedelta
import re
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception
from core.cache import cached_request, invalidate_cache
from .model.model_auth import UserProfile

def login(email: str, password: str) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.moodle_login", level="INFO")

    try:
        url_login = "https://mydy.dypatil.edu/rait/login/index.php"
        payload = {
            "uname_static": email,
            "username": email,
            "uname": email,
            "password": password,
        }

        session = requests.Session()
        logger.info(f"{log_prefix}Attempting Moodle login for {email}")

        response = session.post(
            url_login, data=payload, allow_redirects=True, timeout=15
        )
        html = response.text

        if "Invalid login, please try again" in html:
            logger.warning(f"{log_prefix}Invalid login credentials for {email}")
            return standard_response(
                False, error="Invalid credentials", status_code=401
            )

        if "Academic Status" not in html:
            logger.warning(f"{log_prefix}Unexpected response structure during login.")
            return standard_response(
                False, error="Unexpected login response", status_code=400
            )

        sesskey_match = re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', html)
        sesskey = sesskey_match.group(1) if sesskey_match else None

        if not sesskey:
            logger.warning(f"{log_prefix}Sesskey not found in HTML response.")
            return standard_response(False, error="Sesskey not found", status_code=400)

        user_id_match = re.search(r"/user/profile\.php\?id=(\d+)", html)
        user_id = int(user_id_match.group(1)) if user_id_match else None

        if not user_id:
            logger.warning(f"{log_prefix}User ID not found in HTML response.")
            return standard_response(False, error="User ID not found", status_code=400)

        url_keys = (
            f"https://mydy.dypatil.edu/rait/user/managetoken.php?sesskey={sesskey}"
        )
        logger.info(f"{log_prefix}Fetching security keys for user {user_id}")

        response_keys = session.get(url_keys, timeout=10)
        html_keys = response_keys.text

        soup = BeautifulSoup(html_keys, "html.parser")
        rows = soup.select("table.generaltable tbody tr td.cell.c0")

        keys = [
            cell.get_text(strip=True)
            for cell in rows
            if re.fullmatch(r"[a-fA-F0-9]{32}", cell.get_text(strip=True))
        ]

        while len(keys) < 3:
            keys.append(None)

        web_key, features_key, my_key = keys[:3]

        logger.info(f"{log_prefix}Storing session data in EnvManager")
        EnvManager.set("MOODLE_COOKIE", session.cookies.get("MoodleSession"))
        EnvManager.set("MOODLE_SESSKEY", sesskey)
        EnvManager.set("MOODLE_USER_ID", str(user_id))
        EnvManager.set("MOODLE_WEB_KEY", web_key)
        EnvManager.set("MOODLE_FEATURES_KEY", features_key)
        EnvManager.set("MOODLE_MY_KEY", my_key)

        logger.info(f"{log_prefix}Login successful and data stored in environment")

        result = {
            "user_id": user_id,
            "sesskey": sesskey,
            "cookie": session.cookies.get("MoodleSession"),
            "web_key": web_key,
            "features_key": features_key,
            "my_key": my_key,
        }

        return standard_response(True, data=result, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="moodle_login")


def validate_moodle_token() -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.validate_moodle_token", level="INFO")

    try:
        token: Optional[str] = EnvManager.get("MOODLE_COOKIE", default=None)
        if not token:
            logger.warning(f"{log_prefix}Missing MOODLE_COOKIE in environment.")
            return standard_response(
                success=False,
                error="Missing Moodle token in environment (MOODLE_COOKIE).",
                status_code=400,
            )

        retry_strategy = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504, 408],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        url = "https://mydy.dypatil.edu/rait/my"
        session.cookies.set("MoodleSession", token)

        logger.info(f"{log_prefix}Validating Moodle token via {url}...")
        response = session.get(url, timeout=10)
        response.raise_for_status()

        html = response.text

        if "Academic Status" in html:
            logger.info(f"{log_prefix}Token validation successful.")
            return standard_response(
                success=True,
                data={"valid": True, "url": url},
                status_code=200,
            )

        if "notloggedin" in html or "Login" in html:
            logger.warning(f"{log_prefix}Token appears invalid or expired.")
            return standard_response(
                success=False,
                error="Invalid or expired Moodle token.",
                status_code=401,
            )

        logger.warning(f"{log_prefix}Unable to determine token validity.")
        return standard_response(
            success=False,
            error="Unable to determine Moodle token validity.",
            status_code=400,
        )

    except requests.RequestException as req_err:
        logger.warning(f"{log_prefix}Network or HTTP error: {req_err}")
        return standard_response(
            success=False,
            error=f"Network or request error: {str(req_err)}",
            status_code=502,
        )

    except Exception as exc:
        return handle_exception(logger, exc, context="validate_moodle_token")

def logout() -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.logout_moodle", level="INFO")

    try:
        # Fetch credentials
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        sesskey = EnvManager.get("MOODLE_SESSKEY", default=None)
        logger.info(f"{log_prefix}Initiating logout process...")

        # If sesskey missing, skip logout request but still cleanup
        if not sesskey:
            logger.warning(f"{log_prefix}No sesskey found. Performing cleanup anyway.")
            for key in [
                "MOODLE_COOKIE",
                "MOODLE_SESSKEY",
                "MOODLE_USER_ID",
                "MOODLE_WEB_KEY",
                "MOODLE_FEATURES_KEY",
                "MOODLE_MY_KEY",
            ]:
                try:
                    EnvManager.unset(key)
                    logger.info(f"{log_prefix}Unset environment key: {key}")
                except Exception as e:
                    logger.warning(f"{log_prefix}Failed to unset {key}: {e}")

            return standard_response(
                success=False,
                error="No active Moodle session found. Environment cleared.",
                status_code=400,
            )

        # Attempt Moodle logout
        logout_url = f"https://mydy.dypatil.edu/rait/login/logout.php?sesskey={sesskey}"
        session = requests.Session()
        if token:
            session.cookies.set("MoodleSession", token)

        logger.info(f"{log_prefix}Sending logout request to {logout_url}")
        response = session.get(logout_url, timeout=10)
        response.raise_for_status()

        # Verify if logout succeeded
        logger.info(
            f"{log_prefix}Verifying logout status via validate_moodle_token()..."
        )
        validation_result = validate_moodle_token()

        if validation_result.get("success", False):
            # Token still valid → logout unsuccessful
            logger.warning(f"{log_prefix}Logout request sent, but token still valid.")
            return standard_response(
                success=False,
                error="Logout request failed; session still active.",
                status_code=400,
            )

        # Logout successful — cleanup all Moodle-related env vars
        logger.info(f"{log_prefix}Logout verified. Performing cleanup...")
        for key in [
            "MOODLE_COOKIE",
            "MOODLE_SESSKEY",
            "MOODLE_USER_ID",
            "MOODLE_WEB_KEY",
            "MOODLE_FEATURES_KEY",
            "MOODLE_MY_KEY",
        ]:
            try:
                EnvManager.unset(key)
                logger.info(f"{log_prefix}Unset environment key: {key}")
            except Exception as e:
                logger.warning(f"{log_prefix}Failed to unset {key}: {e}")

        logger.info(f"{log_prefix}Logout successful and environment cleared.")
        return standard_response(
            success=True,
            data={"message": "Logout successful and environment cleared."},
            status_code=200,
        )

    except requests.RequestException as req_err:
        logger.warning(f"{log_prefix}Network or HTTP error during logout: {req_err}")
        return standard_response(
            success=False,
            error="Network or server error during logout.",
            status_code=502,
        )

    except Exception as exc:
        return handle_exception(logger, exc, context="logout_moodle")


def user_profile(refetch: bool = False) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.user_profile", level="INFO")

    try:
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        user_id = EnvManager.get("MOODLE_USER_ID", default=None)

        if not token:
            logger.warning(f"{log_prefix}Missing MOODLE_COOKIE in environment.")
            return standard_response(
                False, error="Missing authentication token", status_code=401
            )

        if not user_id:
            logger.warning(f"{log_prefix}Missing MOODLE_USER_ID in environment.")
            return standard_response(False, error="Missing user ID", status_code=400)

        url = f"https://mydy.dypatil.edu/rait/local/users/profile.php?id={user_id}"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "https://mydy.dypatil.edu/rait/my/",
            "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Cookie": f"MoodleSession={token}; ext_name=ojplmecpdpgccookcobabopnaifgidhf",
        }

        response = cached_request(
            method="GET",
            url=url,
            headers=headers,
            refetch=refetch,
            expire_after=timedelta(hours=1),
            log_prefix=log_prefix,
        )

        if not response or response.status_code != 200:
            logger.warning(
                f"{log_prefix}Invalid response received. Invalidating cache."
            )
            invalidate_cache(response)
            return standard_response(
                False, error="Failed to fetch profile data", status_code=400
            )

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        profile_data: Dict[str, Any] = {}

        profile_parts = soup.select(
            ".profile_parts .userprofilebox .myinfo .schoolinfo tr"
        )
        if profile_parts:
            try:
                profile_data["mob_no"] = (
                    profile_parts[0].select_one(".profile_details").get_text(strip=True)
                    if len(profile_parts) > 0
                    and profile_parts[0].select_one(".profile_details")
                    else None
                )
                profile_data["email_id"] = (
                    profile_parts[1]
                    .select_one(".profile_details a")
                    .get_text(strip=True)
                    if len(profile_parts) > 1
                    and profile_parts[1].select_one(".profile_details a")
                    else None
                )
                profile_data["coll_name"] = (
                    profile_parts[2].select_one(".profile_details").get_text(strip=True)
                    if len(profile_parts) > 2
                    and profile_parts[2].select_one(".profile_details")
                    else None
                )
                profile_data["degree_name"] = (
                    profile_parts[3].select_one(".profile_details").get_text(strip=True)
                    if len(profile_parts) > 3
                    and profile_parts[3].select_one(".profile_details")
                    else None
                )
            except Exception as e:
                logger.warning(f"{log_prefix}Partial profile parts parsing error: {e}")

        personal_table = soup.select_one(".left_info_1 table")
        if personal_table:
            rows = personal_table.find_all("tr")
            mapping = {
                0: "user_name",
                1: "roll_no",
                2: "gender",
                3: "dob",
                4: "postal_code",
                5: "city",
                6: "country",
                7: "religion",
                8: "category",
                9: "father_name",
                10: "mother_name",
                11: "pmob_no",
                12: "femail_id",
                13: "address",
            }
            for idx, row in enumerate(rows):
                key = mapping.get(idx)
                if key:
                    value_span = row.select_one(".profile_td2")
                    profile_data[key] = (
                        value_span.get_text(strip=True) if value_span else None
                    )

        user_obj = UserProfile.from_json(profile_data)
        if not user_obj:
            logger.warning(f"{log_prefix}Incomplete or invalid profile data.")
            invalidate_cache(response)
            return standard_response(
                False, error="Invalid or incomplete profile data", status_code=400
            )

        logger.info(f"{log_prefix}Successfully fetched profile for user_id={user_id}")
        return standard_response(True, data=user_obj.__dict__, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="user_profile")
