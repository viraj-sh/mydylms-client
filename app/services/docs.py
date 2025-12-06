import os
import requests
from typing import Optional, Any, Dict, List
from fastapi.responses import StreamingResponse, RedirectResponse, JSONResponse
from fastapi import HTTPException
from core.utils import EnvManager, standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception
from urllib.parse import urlparse, unquote
import mimetypes
from core.utils import (
    NON_DOWNLOADABLE_MODS,
    NON_VIEWABLE_MODS,
    FRONTEND_VIEWABLE_EXTENSIONS,
    CHUNK_SIZE,
)
from .course import get_course_contents
from .model.model_docs import CourseDocument


def fetch_course_document(
    course_id: int, doc_id: int, action: Optional[str] = None, refetch: bool = False
):
    logger = setup_logging(name="core.fetch_course_document", level="INFO")

    def _stream_file_with_token(
        file_url: str, inline: bool = False
    ) -> StreamingResponse:
        TOKEN = EnvManager.get("MOODLE_COOKIE", default=None)
        if not TOKEN:
            raise HTTPException(
                status_code=401, detail="Missing Moodle session token (TOKEN)"
            )

        parsed = urlparse(file_url)
        filename = unquote(os.path.basename(parsed.path)) or "downloaded_file"

        session = requests.Session()
        session.cookies.set("MoodleSession", TOKEN, domain=parsed.netloc)

        try:
            resp = session.get(file_url, stream=True, timeout=30)
        except requests.RequestException as e:
            raise HTTPException(
                status_code=502, detail=f"Network error while fetching file: {e}"
            )

        if not resp.ok:
            resp.close()
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch file from Moodle ({resp.status_code})",
            )

        content_type = resp.headers.get("Content-Type") or "application/octet-stream"
        content_length = resp.headers.get("Content-Length")

        def _iter_file():
            try:
                for chunk in resp.iter_content(CHUNK_SIZE):
                    if chunk:
                        yield chunk
            finally:
                resp.close()

        disposition_type = "inline" if inline else "attachment"

        headers = {
            "Content-Disposition": f'{disposition_type}; filename="{filename}"',
        }
        if content_length:
            headers["Content-Length"] = content_length

        return StreamingResponse(_iter_file(), media_type=content_type, headers=headers)

    def _guess_media_type(filename: str) -> str:
        mime, _ = mimetypes.guess_type(filename)
        return mime or "application/octet-stream"

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

        mod = getattr(doc, "mod", None)
        doc_name = doc.doc_name or "file"
        file_ext = doc_name.lower().split(".")[-1] if "." in doc_name else ""

        if action == "download":
            if mod in NON_DOWNLOADABLE_MODS:
                return RedirectResponse(url=doc.doc_url)

            moodle_key = EnvManager.get("MOODLE_COOKIE", default=None)
            if not moodle_key:
                return standard_response(
                    False, error="Missing MOODLE_COOKIE in environment", status_code=401
                )
            doc_url = f"{doc.doc_url}?token={moodle_key}"
            if "forcedownload=1" not in doc_url:
                sep = "&" if "?" in doc_url else "?"
                doc_url = f"{doc_url}{sep}forcedownload=1"

            try:
                return _stream_file_with_token(doc_url, inline=False)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Error downloading file: {e}"
                )

        if action == "view":
            if mod in NON_VIEWABLE_MODS:
                # Non-viewable mods (e.g., external links): just redirect to raw doc_url
                return RedirectResponse(url=doc.doc_url)

            if file_ext in FRONTEND_VIEWABLE_EXTENSIONS:
                moodle_key = EnvManager.get("MOODLE_COOKIE", default=None)
                doc_url = (
                    f"{doc.doc_url}?token={moodle_key}" if moodle_key else doc.doc_url
                )
                mime_type = _guess_media_type(doc_name)
                return JSONResponse(
                    content={
                        "status": "success",
                        "data": {
                            "viewer_type": "frontend",
                            "doc_name": doc_name,
                            "mime_type": mime_type,
                            "doc_url": doc_url,
                        },
                        "errors": [],
                    }
                )

            moodle_key = EnvManager.get("MOODLE_COOKIE", default=None)
            if not moodle_key:
                return standard_response(
                    False, error="Missing MOODLE_COOKIE in environment", status_code=401
                )
            doc_url = f"{doc.doc_url}?token={moodle_key}"
            try:
                return _stream_file_with_token(doc_url, inline=True)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Error fetching document: {e}"
                )

        return standard_response(
            False, error=f"Invalid action '{action}'", status_code=400
        )

    except Exception as exc:
        return handle_exception(logger, exc, context="fetch_course_document")
