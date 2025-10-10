import re
from bs4 import BeautifulSoup
from core.utils import fetch_html, OVERALL_TTL, COURSE_TTL, COURSES_TTL
import logging

from core.cache import load_cache, save_cache
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("mydylms")


def det_att(token):
    url = "https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=attendance"
    html = fetch_html(url, token)
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody > tr")
    data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        subject = cells[0].text.strip()
        total = int(cells[1].text.strip() or 0)
        present_cell = cells[2].find("p")
        absent_cell = cells[3].find("p")
        altid = None
        if present_cell and present_cell.has_attr("attenid"):
            altid = int(present_cell["attenid"])
        elif absent_cell and absent_cell.has_attr("attenid"):
            altid = int(absent_cell["attenid"])
        present_str = cells[2].text.strip().replace("--", "")
        absent_str = cells[3].text.strip().replace("--", "")
        perc_str = cells[4].text.strip().replace("--", "")
        data.append(
            {
                "Subject": subject,
                "Total Classes": total,
                "Present": int(present_str) if present_str else None,
                "Absent": int(absent_str) if absent_str else None,
                "Percentage": float(perc_str) if perc_str else None,
                "altid": altid,
            }
        )
    return data


def o_att(token):
    url = (
        "https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=myclasses"
    )
    html = fetch_html(url, token)
    soup = BeautifulSoup(html, "html.parser")
    val = soup.find("p", class_="circular_value")
    if not val:
        return None
    match = re.match(r"(\d+)", val.get_text(strip=True))
    return match.group(1) if match else None


def course_att(token, altid):
    url = f"https://mydy.dypatil.edu/rait/local/attendance/studentreport.php?id={altid}"
    html = fetch_html(url, token)
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody > tr")
    records = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        records.append(
            {
                "Class No": cells[0].text.strip(),
                "Subject": cells[1].text.strip(),
                "Date": cells[2].text.strip(),
                "Time": cells[3].text.strip(),
                "Status": cells[4].text.strip(),
            }
        )
    return records


def get_overall_attendance_helper(token: str):
    cache_name = "attendance_overall"
    cached = load_cache(cache_name, ttl_hours=OVERALL_TTL)
    if cached:
        logger.info("Cache hit: overall attendance")
        return cached

    logger.info("Cache miss: fetching overall attendance")
    data = o_att(token)
    if data:
        save_cache(cache_name, data, ttl_hours=OVERALL_TTL)
    return data


def get_courses_attendance_helper(token: str):
    cache_name = "attendance_courses"
    cached = load_cache(cache_name, ttl_hours=COURSES_TTL)
    if cached:
        logger.info("Cache hit: courses attendance")
        return cached

    logger.info("Cache miss: fetching attendance for all courses")
    data = det_att(token)
    if data:
        save_cache(cache_name, data, ttl_hours=COURSES_TTL)
    return data


def get_course_attendance_helper(token: str, altid: int):
    cache_name = f"attendance_course_{altid}"
    cached = load_cache(cache_name, ttl_hours=COURSE_TTL)
    if cached:
        logger.info(f"Cache hit: course attendance for altid={altid}")
        return cached

    logger.info(f"Cache miss: fetching attendance for course altid={altid}")
    data = course_att(token, altid)
    if data:
        save_cache(cache_name, data, ttl_hours=COURSE_TTL)
    return data
