from fastapi import APIRouter, Query, Path
from fastapi.responses import JSONResponse
from typing import Any, Dict

from core.utils import standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception

from schema.pydantic_semester import (
    GetSemestersRequest,
    GetSemestersResponse,
    SemesterCourseResponse
)

from services.semester import get_semesters, get_courses_in_semester


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


@router.get(
    "/{sem_no}/course",
    response_model=SemesterCourseResponse,
    operation_id="get_courses_in_semester",
)
async def get_courses_in_semester_endpoint(
    sem_no: int = Path(
        ..., description="Semester number (1-indexed or negative for reverse indexing)"
    ),
    refetch: bool = Query(
        False, description="If true, re-fetch semester data bypassing cache."
    ),
) -> JSONResponse:
    logger = setup_logging(name="api.get_courses_in_semester", level="INFO")

    try:
        result = get_courses_in_semester(sem_no=sem_no, refetch=refetch)
        return JSONResponse(content=result, status_code=result.get("status_code", 200))

    except Exception as exc:
        return handle_exception(logger, exc, context="get_courses_in_semester_endpoint")
