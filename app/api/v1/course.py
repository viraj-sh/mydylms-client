from fastapi import APIRouter, Path, Query
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import ValidationError
from core.logging import setup_logging
from core.exceptions import handle_exception
from core.utils import standard_response
from services.course import get_course_contents  
from schema.pydantic_course import CourseDocsRequestModel, StandardResponseModel, CourseSectionModel

router = APIRouter(
    prefix="/course",
    tags=["Course"],
)

logger = setup_logging(name="core.course_contents_endpoint")


@router.get(
    "/{course_id}/docs",
    operation_id="get_course_docs",
    response_model=StandardResponseModel,
)
async def get_course_docs(
    course_id: int = Path(..., description="Numeric Moodle course id", ge=1),
    refetch: Optional[bool] = Query(
        False, description="If true, bypass cache and refetch from Moodle"
    ),
):

    try:
        try:
            req = CourseDocsRequestModel(course_id=course_id, refetch=refetch)
        except ValidationError as vex:
            resp = standard_response(success=False, error=str(vex), status_code=422)
            return JSONResponse(content=resp, status_code=resp.get("status_code", 422))

        result = get_course_contents(course_id=req.course_id, refetch=bool(req.refetch))

        if not isinstance(result, dict):
            result = standard_response(
                success=False, error="Invalid internal response", status_code=500
            )

        status_code = int(result.get("status_code", 200))
        return JSONResponse(content=result, status_code=status_code)

    except Exception as exc:
        return handle_exception(logger, exc, context="get_course_docs")
