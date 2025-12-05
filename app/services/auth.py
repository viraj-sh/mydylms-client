from typing import Optional, Any, Dict
from datetime import timedelta
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception


def login(user_email: str, password: str) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.moodle_login", level="INFO")

    try:
        # --- Step 1: Initial login ---
        url_login = "https://mydy.dypatil.edu/rait/login/index.php"
        payload = {
            "uname_static": user_email,
            "username": user_email,
            "uname": user_email,
            "password": password,
        }

        session = requests.Session()
        logger.info(f"{log_prefix}Attempting Moodle login for {user_email}")

        response = session.post(
            url_login, data=payload, allow_redirects=True, timeout=15
        )
        html = response.text

        if "Invalid login, please try again" in html:
            logger.warning(f"{log_prefix}Invalid login credentials for {user_email}")
            return standard_response(
                False, error="Invalid credentials", status_code=401
            )

        if "Academic Status" not in html:
            logger.warning(f"{log_prefix}Unexpected response structure during login.")
            return standard_response(
                False, error="Unexpected login response", status_code=400
            )

        # --- Step 2: Extract sesskey ---
        sesskey_match = re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', html)
        sesskey = sesskey_match.group(1) if sesskey_match else None

        if not sesskey:
            logger.warning(f"{log_prefix}Sesskey not found in HTML response.")
            return standard_response(False, error="Sesskey not found", status_code=400)

        # --- Step 3: Extract user_id ---
        user_id_match = re.search(r"/user/profile\.php\?id=(\d+)", html)
        user_id = int(user_id_match.group(1)) if user_id_match else None

        if not user_id:
            logger.warning(f"{log_prefix}User ID not found in HTML response.")
            return standard_response(False, error="User ID not found", status_code=400)

        # --- Step 4: Fetch security keys ---
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

        # Pad to 3 elements if fewer found
        while len(keys) < 3:
            keys.append(None)

        web_key, features_key, my_key = keys[:3]

        # --- Step 5: Store everything in EnvManager ---
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
