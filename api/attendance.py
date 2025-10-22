from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from os import getenv
from schema.pydantic_attendance import (
    OverallAttendanceResponse,
    CoursesAttendanceResponse,
    CourseAttendanceResponse,
)
from core.attendance import (
    get_overall_attendance_helper,
    get_courses_attendance_helper,
    get_course_attendance_helper,
)
from core.utils import ENV_FILE

router = APIRouter(prefix="/att", tags=["Attendance"])


@router.get(
    "/",
    summary="Get overall attendance",
    response_model=OverallAttendanceResponse,
    operation_id="get_overall_attendance",
)
def get_overall_attendance():
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="User not logged in")

    data = get_overall_attendance_helper(token)
    if data is None:
        raise HTTPException(
            status_code=500, detail="Failed to fetch overall attendance"
        )

    return OverallAttendanceResponse(status="success", data=data, errors=[])


@router.get(
    "/courses",
    summary="Get attendance for all courses",
    response_model=CoursesAttendanceResponse,
    operation_id="get_all_course_attendance",
)
def get_courses_attendance():
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="User not logged in")

    data = get_courses_attendance_helper(token)
    if not data:
        raise HTTPException(
            status_code=500, detail="Failed to fetch courses attendance"
        )

    return CoursesAttendanceResponse(status="success", data=data, errors=[])


@router.get(
    "/course/{altid}",
    summary="Get attendance for a given course",
    response_model=CourseAttendanceResponse,
    operation_id="get_course_attendance",
)
def get_course_attendance(altid: int):
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="User not logged in")

    data = get_course_attendance_helper(token, altid)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch course attendance")

    return CourseAttendanceResponse(status="success", data=data, errors=[])
