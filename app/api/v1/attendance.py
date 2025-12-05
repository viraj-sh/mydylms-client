from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional
from core.logging import setup_logging
from core.exceptions import handle_exception
from core.utils import standard_response
from services.attendance import fetch_attendance, course_att 
from schema.pydantic_attendance import AttendanceResponseModel, CourseAttendanceResponse

router = APIRouter(prefix="/attendance", tags=["Attendance"])
logger = setup_logging(name="attendance_router")


@router.get(
    "/overall",
    response_model=AttendanceResponseModel,
    operation_id="get_overall_attendance",
)
async def get_overall_attendance(
    refetch: Optional[bool] = Query(False, description="Set true to bypass cache")
):
    try:
        result = fetch_attendance(refetch=refetch)
        return JSONResponse(content=result, status_code=result.get("status_code", 200))

    except Exception as exc:
        return handle_exception(logger, exc, context="get_overall_attendance")


@router.get(
    "/attendance/course/{alt_id}",
    response_model=CourseAttendanceResponse,
    operation_id="getCourseAttendance",
)
def get_course_attendance(
    alt_id: str,
    refetch: bool = Query(
        default=False, description="If true, bypass cache and fetch fresh attendance."
    ),
) -> JSONResponse:
    try:
        result: Dict[str, Any] = course_att(altid=alt_id, refetch=refetch)
        return JSONResponse(content=result, status_code=result.get("status_code", 200))

    except Exception as exc:
        error_response = handle_exception(logger, exc, context="get_course_attendance")
        return JSONResponse(
            content=error_response, status_code=error_response.get("status_code", 500)
        )
