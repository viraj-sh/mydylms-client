from typing import Optional, Any, Dict, List
from datetime import timedelta
from fastapi.responses import StreamingResponse, RedirectResponse
from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.cache import cached_request, invalidate_cache
from core.exceptions import handle_exception
from .course import get_course_contents

def fetch_course_document(
    course_id: int, doc_id: int, action: Optional[str] = None, refetch: bool = False
):
    logger = setup_logging(name="core.fetch_course_document", level="INFO")
    log_prefix = "[MoodleAPI] "

    try:
        course_resp = get_course_contents(course_id=course_id, refetch=refetch)

        if not course_resp.get("success"):
            return standard_response(
                success=False, error="Failed to fetch course contents", status_code=400
            )

        all_weeks: List[Dict[str, Any]] = course_resp.get("data", [])
        if not isinstance(all_weeks, list):
            return standard_response(
                False, error="Malformed course contents", status_code=500
            )

        found_doc_data: Optional[Dict[str, Any]] = None
        for week in all_weeks:
            docs = week.get("docs", [])
            for d in docs:
                if d.get("doc_id") == doc_id:
                    found_doc_data = d
                    break
            if found_doc_data:
                break

        if not found_doc_data:
            return standard_response(
                False,
                error=f"Document {doc_id} not found in course {course_id}",
                status_code=404,
            )

        doc = CourseDocument.from_json(found_doc_data)
        if not doc:
            return standard_response(
                False,
                error="Document data malformed or missing required fields",
                status_code=500,
            )

        if action is None:
            return standard_response(True, data=found_doc_data, status_code=200)

        moodle_key = EnvManager.get("MOODLE_WEB_KEY", default=None)
        logger.info(f"{log_prefix}Using MOODLE_WEB_KEY")

        if not moodle_key:
            return standard_response(
                False, error="Missing MOODLE_WEB_KEY in environment", status_code=401
            )

        file_url = f"{doc.doc_url}?token={moodle_key}"

        resp = cached_request(
            url=file_url,
            method="GET",
            headers={},
            expire_after=timedelta(hours=1),
            allow_redirects=True,
            refetch=refetch,
            log_prefix=log_prefix,
        )

        if not resp or resp.status_code != 200:
            invalidate_cache(resp)
            return standard_response(
                False, error="Failed to fetch document from Moodle", status_code=400
            )

        content_type = resp.headers.get("Content-Type", "application/octet-stream")
        filename = doc.doc_name or "file"
        disposition = "inline" if action == "view" else "attachment"

        def file_stream():
            for chunk in resp.iter_content(8192):
                if chunk:
                    yield chunk

        return StreamingResponse(
            file_stream(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'{disposition}; filename="{filename}"',
                "Cache-Control": "no-store",
            },
        )

    except Exception as exc:
        return handle_exception(logger, exc, context="fetch_course_document")
