import re
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.utils import fetch_html
from dotenv import set_key, load_dotenv
from core.utils import ENV_FILE, DATA_DIR
from core.cache import save_cache
import logging
from core.logging_config import setup_logging
import shutil

setup_logging()
logger = logging.getLogger("mydylms")


def moodle_login(user_email: str, password: str):
    url = "https://mydy.dypatil.edu/rait/login/index.php"
    payload = {
        "uname_static": user_email,
        "username": user_email,
        "uname": user_email,
        "password": password,
    }

    session = requests.Session()
    try:
        response = session.post(url, data=payload, allow_redirects=True)
        html = response.text
    except requests.RequestException:
        return {
            "status": "error",
            "cookie": None,
            "sesskey": None,
            "semesters": None,
            "user_id": None,
        }

    if "Invalid login, please try again" in html:
        status = "invalid credentials"
    elif "Academic Status" in html or "Dashboard" in html or "My courses" in html:
        status = "success"
    else:
        status = "unknown"

    if status != "success":
        return {
            "status": status,
            "cookie": None,
            "sesskey": None,
            "semesters": None,
            "user_id": None,
        }

    cookie = session.cookies.get("MoodleSession")
    if not cookie:
        return {
            "status": "error",
            "cookie": None,
            "sesskey": None,
            "semesters": None,
            "user_id": None,
        }

    headers = {"Cookie": f"MoodleSession={cookie}"}
    try:
        my_response = session.get("https://mydy.dypatil.edu/rait/my", headers=headers)
        my_html = my_response.text
    except requests.RequestException:
        return {
            "status": "error",
            "cookie": cookie,
            "sesskey": None,
            "semesters": None,
            "user_id": None,
        }

    sesskey_match = re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', my_html)
    sesskey = sesskey_match.group(1) if sesskey_match else None

    user_id_match = re.search(r"/user/profile\.php\?id=(\d+)", my_html)
    user_id = int(user_id_match.group(1)) if user_id_match else None

    soup = BeautifulSoup(my_html, "html.parser")
    semesters = []
    for li in soup.find_all("li", class_="type_course"):
        span = li.find("span", class_="usdimmed_text")
        if not span:
            continue
        semester_name = span.get_text(strip=True)
        if not re.fullmatch(
            r"Semester\s+[IVX0-9]+", semester_name, flags=re.IGNORECASE
        ):
            continue
        p_tag = span.find_parent("p")
        ul_tag = p_tag.find_next_sibling("ul") if p_tag else None
        if not ul_tag:
            ul_tag = li.find("ul")
        if not ul_tag:
            continue
        subjects = []
        for subject_li in ul_tag.find_all("li", recursive=False):
            a_tag = subject_li.find("a", href=True)
            if not a_tag:
                continue
            parsed_url = urlparse(a_tag["href"])
            query = parse_qs(parsed_url.query)
            if "/course/view.php" in parsed_url.path and "id" in query:
                subjects.append(
                    {"name": a_tag.get_text(strip=True), "id": int(query["id"][0])}
                )
        if subjects:
            semesters.append({"semester": semester_name, "subjects": subjects})

    return {
        "status": status,
        "cookie": cookie,
        "sesskey": sesskey,
        "user_id": user_id,
        "semesters": semesters,
    }


def validate_token(token: str) -> bool:
    url = "https://mydy.dypatil.edu/rait/my"
    try:
        html = fetch_html(url, token)
    except requests.RequestException:
        return False
    if "Academic Status" in html:
        return True
    if "notloggedin" in html or "Login" in html:
        return False
    return False


def get_security_keys(token: str, sesskey: str):
    url = f"https://mydy.dypatil.edu/rait/user/managetoken.php?sesskey={sesskey}"
    try:
        html = fetch_html(url, token)
    except requests.RequestException:
        return {"web_key": None, "features_key": None, "my_key": None}

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.generaltable tbody tr td.cell.c0")
    keys = [
        cell.get_text(strip=True)
        for cell in rows
        if re.fullmatch(r"[a-fA-F0-9]{32}", cell.get_text(strip=True))
    ]
    if len(keys) < 3:
        keys += [None] * (3 - len(keys))
    return {
        "web_key": keys[0],
        "features_key": keys[1],
        "my_key": keys[2],
    }


def get_sesskey(token: str):
    url = "https://mydy.dypatil.edu/rait/my"
    try:
        html = fetch_html(url, token)
    except requests.RequestException:
        return None

    sesskey_match = re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', html)
    return sesskey_match.group(1) if sesskey_match else None


def get_user_id(token: str):
    url = "https://mydy.dypatil.edu/rait/my"
    try:
        html = fetch_html(url, token)
    except requests.RequestException:
        return None

    user_id_match = re.search(r"/user/profile\.php\?id=(\d+)", html)
    return int(user_id_match.group(1)) if user_id_match else None


def logout(token: str, sesskey: str):
    url = f"https://mydy.dypatil.edu/rait/login/logout.php?sesskey={sesskey}"
    session = requests.Session()
    session.cookies.set("MoodleSession", token)

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def login_helper(user_email: str, password: str) -> dict:
    result = moodle_login(user_email, password)

    if result["status"] == "success":
        # Save semesters cache
        if result.get("semesters"):
            save_cache("semesters", result["semesters"], ttl_hours=6)

        load_dotenv(ENV_FILE)
        set_key(str(ENV_FILE), "USER_ID", str(result["user_id"]))
        set_key(str(ENV_FILE), "TOKEN", result["cookie"] or "")
        set_key(str(ENV_FILE), "SESSKEY", result["sesskey"] or "")

    return result


def get_creds_helper() -> dict:
    load_dotenv(ENV_FILE)

    token = os.getenv("TOKEN")
    user_id = os.getenv("USER_ID")
    sesskey = os.getenv("SESSKEY")
    web_key = os.getenv("KEY_1")
    features_key = os.getenv("KEY_2")
    my_key = os.getenv("KEY_3")

    # Only fetch user_id if missing
    if not user_id and token:
        fetched_user_id = get_user_id(token)
        if fetched_user_id:
            set_key(str(ENV_FILE), "USER_ID", str(fetched_user_id))
            user_id = str(fetched_user_id)

    # Only fetch sesskey if missing
    if not sesskey and token:
        fetched_sesskey = get_sesskey(token)
        if fetched_sesskey:
            set_key(str(ENV_FILE), "SESSKEY", fetched_sesskey)
            sesskey = fetched_sesskey

    # Only fetch keys if any of them is missing
    if token and (not web_key or not features_key or not my_key):
        keys = get_security_keys(token, sesskey)
        logger.info(f"Fetched security keys: {keys}")
        if keys.get("web_key") and not web_key:
            set_key(str(ENV_FILE), "KEY_1", keys["web_key"])
            web_key = keys["web_key"]
        if keys.get("features_key") and not features_key:
            set_key(str(ENV_FILE), "KEY_2", keys["features_key"])
            features_key = keys["features_key"]
        if keys.get("my_key") and not my_key:
            set_key(str(ENV_FILE), "KEY_3", keys["my_key"])
            my_key = keys["my_key"]

    return {
        "token": token,
        "user_id": int(user_id) if user_id else None,
        "sesskey": sesskey,
        "keys": {
            "web_key": web_key,
            "features_key": features_key,
            "my_key": my_key,
        },
    }


def logout_helper(token: str, sesskey: str) -> bool:
    success = logout(token, sesskey)
    if not success:
        return False

    # Remove the .env file if it exists
    if ENV_FILE.exists():
        ENV_FILE.unlink()

        # Remove cached env vars from process memory
    for key in ["TOKEN", "USER_ID", "SESSKEY", "KEY_1", "KEY_2", "KEY_3"]:
        os.environ.pop(key, None)

    # Remove the entire data directory if it exists
    if DATA_DIR.exists() and DATA_DIR.is_dir():
        shutil.rmtree(DATA_DIR)

    return True
