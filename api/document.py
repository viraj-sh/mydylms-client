from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from schema.pydantic_document import DocumentResponse
from core.docs import (
    get_doc_details_by_view_id,
    _guess_extension,
    _guess_media_type,
    _download_with_token,
    _build_streaming_response,
)
import requests
import mimetypes
import io
from core.utils import (
    NON_DOWNLOADABLE_MODS,
    NON_VIEWABLE_MODS,
    FRONTEND_VIEWABLE_EXTENSIONS,
)
import os

from fastapi.responses import JSONResponse


router = APIRouter(prefix="/doc", tags=["Document"])


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Document metadata, view or download handler",
)
def handle_document(
    doc_id: int,
    action: str | None = Query(default=None, description="view | download | None"),
):
    try:
        doc = get_doc_details_by_view_id(doc_id)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Document database not found: {e}. Try syncing course data first.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while accessing document: {str(e)}",
        )

    if not doc:
        raise HTTPException(status_code=404, detail=f"Document id {doc_id} not found")

    mod = doc.get("mod")
    doc_url = doc.get("doc_url")
    doc_name = doc.get("doc_name", "")
    file_ext = _guess_extension(doc_name)

    # ✅ If no action, just return metadata
    if action is None:
        return {"status": "success", "data": doc, "errors": []}

    # ✅ Handle "view"
    if action == "view":
        if mod in NON_VIEWABLE_MODS:
            return RedirectResponse(url=doc_url)

        if file_ext in FRONTEND_VIEWABLE_EXTENSIONS:
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

        try:
            filename, content = _download_with_token(doc_url)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching document: {e}")

        return _build_streaming_response(filename, content, inline=True)

    # ✅ Handle "download"
    elif action == "download":
        if mod in NON_DOWNLOADABLE_MODS:
            return RedirectResponse(url=doc_url)

        if "forcedownload=1" not in doc_url:
            sep = "&" if "?" in doc_url else "?"
            doc_url = f"{doc_url}{sep}forcedownload=1"

        try:
            filename, content = _download_with_token(doc_url)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error downloading file: {e}")

        return _build_streaming_response(filename, content, inline=False)

    raise HTTPException(
        status_code=400,
        detail="Invalid action parameter. Use 'view' or 'download'.",
    )
