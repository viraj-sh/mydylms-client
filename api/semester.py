from fastapi import APIRouter, HTTPException
from schema.pydantic_semester import SemestersResponse, CourseResponse
from core.info import get_semesters_helper
from core.course import get_course_contents_helper
from dotenv import load_dotenv
from os import getenv
from core.utils import ENV_FILE

router = APIRouter(prefix="/sem", tags=["Semester"])


@router.get("/", summary="Get all semesters", response_model=SemestersResponse)
def get_all_semesters():
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="User not logged in")

    semesters = get_semesters_helper(token)
    if not semesters:
        raise HTTPException(status_code=500, detail="Failed to fetch semesters")

    return SemestersResponse(status="success", data=semesters, errors=[])


@router.get(
    "/{course_id}/course", summary="Get course contents", response_model=CourseResponse
)
def get_course_contents(course_id: int):
    load_dotenv(ENV_FILE)
    key = getenv("KEY_1") or getenv("KEY_2")
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key (token)")

    course_data = get_course_contents_helper(key, course_id)
    if not course_data:
        raise HTTPException(status_code=500, detail="Failed to fetch course contents")

    return CourseResponse(status="success", data=course_data, errors=[])
