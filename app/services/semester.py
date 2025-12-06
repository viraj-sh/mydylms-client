import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from datetime import timedelta

from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.cache import cached_request, invalidate_cache
from core.exceptions import handle_exception
from .model.model_semester import Semester


def get_semesters(refetch: bool = False) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.get_semesters", level="INFO")
    url = "https://mydy.dypatil.edu/rait/my"

    try:
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        if not token:
            logger.warning(f"{log_prefix} Missing Moodle session token in environment.")
            return standard_response(
                success=False,
                error="Missing Moodle session token (MOODLE_COOKIE).",
                status_code=400,
            )

        cookies = {"MoodleSession": token}

        response = cached_request(
            "GET",
            url,
            cookies=cookies,
            expire_after=timedelta(hours=1),
            refetch=refetch,
        )

        if not response or response.status_code != 200 or not response.text:
            logger.warning(f"{log_prefix} Invalid or empty response received.")
            invalidate_cache(response)
            return standard_response(
                success=False,
                error="Failed to fetch semester data.",
                status_code=400,
            )

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        semesters: List[Dict[str, Any]] = []

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
                    try:
                        subject_entry = {
                            "name": a_tag.get_text(strip=True),
                            "id": int(query["id"][0]),
                        }
                        subjects.append(subject_entry)
                    except (KeyError, ValueError):
                        continue

            if subjects:
                semesters.append({"semester": semester_name, "subjects": subjects})

        parsed_semesters = []
        for s in semesters:
            parsed = Semester.from_json(s)
            if parsed:
                parsed_semesters.append(parsed)

        if not parsed_semesters:
            logger.warning(f"{log_prefix} No valid semester data parsed.")
            invalidate_cache(response)
            return standard_response(
                success=False,
                error="No valid semester data found.",
                status_code=400,
            )

        logger.info(
            f"{log_prefix} Successfully fetched {len(parsed_semesters)} semesters."
        )
        result = [s.to_dict() for s in parsed_semesters]
        return standard_response(success=True, data=result, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="get_semesters")


def get_courses_in_semester(sem_no: int, refetch: bool = False) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.get_courses_in_semester", level="INFO")

    try:
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        if not token:
            logger.warning(f"{log_prefix}Missing Moodle token in environment.")
            return standard_response(False, error="User not logged in", status_code=401)

        semesters_response = get_semesters(refetch=refetch)
        if not semesters_response.get("success", False):
            logger.warning(
                f"{log_prefix}Failed to fetch semesters: {semesters_response.get('error')}"
            )
            return standard_response(
                False, error="Failed to fetch semesters", status_code=500
            )

        semesters_data = semesters_response.get("data")
        if not isinstance(semesters_data, list):
            logger.warning(f"{log_prefix}Invalid semesters data structure.")
            return standard_response(
                False, error="Invalid semesters data structure", status_code=500
            )

        if len(semesters_data) == 0:
            logger.info(f"{log_prefix}No semesters found for the user.")
            return standard_response(False, error="No semesters found", status_code=404)

        total = len(semesters_data)

        index = total + sem_no if sem_no < 0 else sem_no - 1
        if index < 0 or index >= total:
            logger.warning(f"{log_prefix}Invalid semester number: {sem_no}")
            return standard_response(
                False, error="Invalid semester number", status_code=400
            )

        semester = semesters_data[index]
        logger.info(
            f"{log_prefix}Fetched semester data successfully for sem_no={sem_no}"
        )

        return standard_response(True, data=semester, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="get_courses_in_semester")
