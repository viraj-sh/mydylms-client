import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from core.utils import fetch_html


def get_semesters(token: str):
    url = "https://mydy.dypatil.edu/rait/my"
    html = fetch_html(url, token)
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

    return semesters


def user_profile(token: str, user_id: int):
    url = f"https://mydy.dypatil.edu/rait/user/profile.php?id={user_id}"

    try:
        html = fetch_html(url, token)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(html, "html.parser")
    profile_data = {}
    profile_parts = soup.select(".profile_parts .userprofilebox .myinfo .schoolinfo tr")
    if profile_parts:
        try:
            profile_data["mob_no"] = (
                profile_parts[0].select_one(".profile_details").get_text(strip=True)
            )
            profile_data["email_id"] = (
                profile_parts[1].select_one(".profile_details a").get_text(strip=True)
            )
            profile_data["coll_name"] = (
                profile_parts[2].select_one(".profile_details").get_text(strip=True)
            )
            profile_data["degree_name"] = (
                profile_parts[3].select_one(".profile_details").get_text(strip=True)
            )
        except IndexError:
            pass
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

    return profile_data
