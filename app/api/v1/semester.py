from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Any, Dict

from core.utils import standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception

from schema.pydantic_semester import (
    GetSemestersRequest,
    GetSemestersResponse,
)

from services.semester import get_semesters


router = APIRouter(
    prefix="/sem",
    tags=["Semesters"],
)


@router.get(
    "/",
    response_model=GetSemestersResponse,
    operation_id="get_semesters_list",
)
async def get_semesters_endpoint(
    refetch: bool = Query(
        False,
        description="If true, bypass cache and refetch data directly from Moodle.",
    )
) -> JSONResponse:
    logger = setup_logging(name="api.get_semesters", level="INFO")

    try:
        result: Dict[str, Any] = get_semesters(refetch=refetch)
        if not isinstance(result, dict) or "status_code" not in result:
            logger.warning("[MoodleAPI] Invalid response format from get_semesters()")
            result = standard_response(
                success=False,
                error="Internal format error in get_semesters().",
                status_code=500,
            )
        return JSONResponse(content=result, status_code=result.get("status_code", 200))

    except Exception as exc:
        return handle_exception(logger, exc, context="get_semesters_endpoint")
