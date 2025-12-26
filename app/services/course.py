from typing import Any, Dict, List
from datetime import timedelta
import re
from dataclasses import asdict

from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.cache import cached_request, invalidate_cache
from core.exceptions import handle_exception
from .model.model_course import CourseDocument, CourseSection


def get_course_contents(course_id: int, refetch: bool = False) -> Dict[str, Any]:
    log_prefix = "[MoodleAPI] "
    logger = setup_logging(name="core.get_course_contents", level="INFO")

    try:
        key = EnvManager.get("MOODLE_WEB_KEY", default=None)
        if not key:
            logger.warning(f"{log_prefix}Missing MOODLE_WEB_KEY in environment.")
            return standard_response(
                False, error="Missing Moodle API key", status_code=400
            )

        url = "https://mydy.dypatil.edu/rait/webservice/rest/server.php"
        params = {
            "wstoken": key,
            "wsfunction": "core_course_get_contents",
            "moodlewsrestformat": "json",
            "courseid": int(course_id),
        }

        response = cached_request(
            method="POST",
            url=url,
            data=params,
            expire_after=timedelta(hours=1),
            refetch=refetch,
            log_prefix=log_prefix,
        )

        if not response or response.status_code != 200:
            invalidate_cache(response)
            return standard_response(
                False, error="Invalid API response", status_code=400
            )

        try:
            data = response.json()
        except ValueError:
            invalidate_cache(response)
            return standard_response(
                False, error="Failed to decode JSON", status_code=400
            )

        if isinstance(data, dict) and "exception" in data:
            invalidate_cache(response)
            error_info = {
                "errorcode": data.get("errorcode"),
                "message": data.get("message"),
            }
            logger.warning(f"{log_prefix}Moodle API exception: {error_info}")
            return standard_response(False, error=error_info, status_code=400)

        if not isinstance(data, list):
            invalidate_cache(response)
            return standard_response(
                False, error="Unexpected API response format", status_code=400
            )

        formatted_sections: List[CourseSection] = []
        for section in data:
            if not isinstance(section, dict):
                continue

            week_name = section.get("name")
            docs: List[CourseDocument] = []

            for module in section.get("modules", []):
                modname = module.get("modname")
                doc_name_module = module.get("name")
                view_id = module.get("id")

                for content in module.get("contents", []):
                    doc_url = content.get("fileurl")
                    doc_id = None

                    if doc_url and doc_url.startswith(
                        "https://mydy.dypatil.edu/rait/webservice/pluginfile.php"
                    ):
                        match = re.search(r"pluginfile\.php/(\d+)/", doc_url)
                        if match:
                            doc_id = int(match.group(1))
                        doc_url = doc_url.replace("webservice/", "")
                        if doc_url.endswith("?forcedownload=1"):
                            doc_url = doc_url.replace("?forcedownload=1", "")

                    doc = CourseDocument.from_json(
                        {
                            "course_id": course_id,
                            "view_id": view_id,
                            "doc_id": doc_id,
                            "module": doc_name_module,
                            "mod": modname,
                            "type": content.get("type"),
                            "doc_name": content.get("filename"),
                            "doc_size": content.get("filesize"),
                            "doc_url": doc_url,
                            "time": content.get("timemodified"),
                        }
                    )
                    if doc:
                        docs.append(doc)

            formatted_sections.append(CourseSection(week=week_name, docs=docs))

        data_to_return = [asdict(section) for section in formatted_sections]

        return standard_response(True, data=data_to_return, status_code=200)

    except Exception as exc:
        return handle_exception(logger, exc, context="get_course_contents")
