import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.utils import fetch_html


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
    elif "Academic Status" in html:
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

    sesskey_match = re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', html)
    sesskey = sesskey_match.group(1) if sesskey_match else None

    soup = BeautifulSoup(html, "html.parser")

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

    user_id_match = re.search(r"/user/profile\.php\?id=(\d+)", html)
    user_id = int(user_id_match.group(1)) if user_id_match else None

    return {
        "status": status,
        "cookie": session.cookies.get("MoodleSession"),
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
