from typing import Optional
from fastapi import APIRouter, Query, Path
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from core.logging import setup_logging
from core.exceptions import handle_exception
from core.utils import standard_response
from services.docs import fetch_course_document
from schema.pydantic_docs import StandardResponseModel, CourseDocumentModel

router = APIRouter(prefix="/api", tags=["Documents"])

logger = setup_logging(name="api.doc_router", level="INFO")



@router.get(
    "/course/{course_id}/doc",
    operation_id="getCourseDocument",
    response_model=StandardResponseModel,
    responses={
        200: {
            "description": "Standard response (metadata) or file stream (view/download)"
        },
        400: {"description": "Bad request / error"},
        401: {"description": "Unauthorized / missing key"},
        404: {"description": "Document not found"},
    },
)
def get_document_endpoint(
    course_id: int = Path(..., description="Course ID"),
    doc_id: int = Query(..., description="Document ID to fetch"),
    action: Optional[str] = Query(
        None,
        description="Use 'view' for inline, 'download' for attachment. Leave empty for metadata.",
    ),
    refetch: Optional[bool] = Query(False, description="Bypass cache if true"),
):
    try:
        logger.info(
            f"[API] Request doc={doc_id} from course={course_id} (action={action}, refetch={refetch})"
        )

        result = fetch_course_document(
            course_id=course_id,
            doc_id=doc_id,
            action=action,
            refetch=refetch,
        )

        if isinstance(result, StreamingResponse):
            logger.info(f"[API] Returning stream for doc {doc_id}")
            return result

        if isinstance(result, dict):
            status_code = int(result.get("status_code", 200))
            return JSONResponse(content=result, status_code=status_code)

        logger.warning(f"[API] Unexpected return type from backend: {type(result)}")
        fallback = standard_response(
            False, error="Unexpected response from backend", status_code=500
        )
        return JSONResponse(content=fallback, status_code=500)

    except Exception as exc:
        return handle_exception(logger, exc, context="get_document_endpoint")
