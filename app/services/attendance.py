import re
from typing import Optional, Dict, Any
from datetime import timedelta
from bs4 import BeautifulSoup 
from datetime import timedelta
from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.cache import cached_request, invalidate_cache
from core.exceptions import handle_exception
from .model.model_attendance import (
    AttendanceData,
    AttendanceRecord,
    CourseAttendanceRecord,
)


def fetch_attendance(refetch: bool = False) -> Dict[str, Any]:
    logger = setup_logging(name="core.fetch_attendance", level="INFO")
    log_prefix = "[AcademicAPI] "
    try:
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        if not token:
            logger.warning(f"{log_prefix}MOODLE_COOKIE not set in environment.")
            return standard_response(
                False, error="Missing MOODLE_COOKIE", status_code=400
            )

        url = "https://mydy.dypatil.edu/rait/blocks/academic_status/ajax.php?action=attendance"

        response = cached_request(
            url=url,
            method="GET",
            headers={"Cookie": f"MoodleSession={token}"},
            expire_after=timedelta(hours=1),
            refetch=refetch,
        )

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("tbody > tr")
        records: List[AttendanceRecord] = []

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

            record_dict = {
                "Subject": subject,
                "Total Classes": total,
                "Present": int(present_str) if present_str else None,
                "Absent": int(absent_str) if absent_str else None,
                "Percentage": float(perc_str) if perc_str else None,
                "altid": altid,
            }

            record = AttendanceRecord.from_json(record_dict)
            if record:
                records.append(record)

        if not records:
            logger.warning(
                f"{log_prefix}No valid attendance records found, invalidating cache."
            )
            invalidate_cache(response)
            return standard_response(
                False, error="Failed to fetch attendance data", status_code=400
            )

        total_classes = sum(
            r.Total_Classes for r in records if r.Total_Classes is not None
        )
        total_present = sum(r.Present for r in records if r.Present is not None)
        overall_percentage = (
            (total_present / total_classes * 100) if total_classes > 0 else 0.0
        )

        result = {
            "overall_total_classes": total_classes,
            "overall_present": total_present,
            "overall_percentage": round(overall_percentage, 2),
            "records": [r.__dict__ for r in records],
        }

        return standard_response(True, data=result, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="fetch_attendance")

def course_att(altid: str, refetch: bool = False) -> Dict[str, Any]:
    logger = setup_logging(name="core.course_att", level="INFO")
    log_prefix = "[AcademicAPI] "
    try:
        token = EnvManager.get("MOODLE_COOKIE", default=None)
        if not token:
            return standard_response(
                success=False,
                error="Missing session cookie (MOODLE_COOKIE).",
                status_code=400,
            )

        url = f"https://mydy.dypatil.edu/rait/local/attendance/studentreport.php?id={altid}"

        response = cached_request(
            method="GET",
            url=url,
            headers={"Cookie": f"MoodleSession={token}"},
            expire_after=timedelta(hours=1),
            refetch=refetch,
            log_prefix="[Attendance] ",
        )

        if not response or response.status_code != 200 or not response.text:
            invalidate_cache(response)
            return standard_response(
                success=False,
                error="Failed to retrieve attendance page.",
                status_code=400,
            )

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("tbody > tr")

        attendance_records: List[Dict[str, Any]] = []

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue
            status_cell = cells[4]
            span = status_cell.find("span")
            status_text = span.text.strip() if span else status_cell.text.strip()

            raw_record = {
                "Class No": cells[0].text.strip(),
                "Subject": cells[1].text.strip(),
                "Date": cells[2].text.strip(),
                "Time": cells[3].text.strip(),
                "Status": status_text,
            }

            record = CourseAttendanceRecord.from_json(raw_record)
            if record:
                attendance_records.append(record.__dict__)
            else:
                logger.warning("Skipping malformed record: %s", raw_record)

        return standard_response(
            success=True, data={"attendance": attendance_records}, status_code=200
        )

    except Exception as exc:
        return handle_exception(logger, exc, context="course_att")
