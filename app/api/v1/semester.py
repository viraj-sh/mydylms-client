from fastapi import APIRouter, HTTPException
from schema.pydantic_semester import SemestersResponse, SemesterCoursesResponse
from core.info import get_semesters_helper
from dotenv import load_dotenv
from os import getenv
from core.utils import ENV_FILE

router = APIRouter(prefix="/sem", tags=["Semester"])


@router.get(
    "/",
    summary="Get all semesters",
    response_model=SemestersResponse,
    operation_id="get_all_semesters",
)
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
    "/{sem_no}/course",
    summary="Get all courses in a given semester",
    response_model=SemesterCoursesResponse,
    operation_id="get_semester_courses",
)
def get_courses_in_semester(sem_no: int):
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="User not logged in")

    semesters = get_semesters_helper(token)
    if not isinstance(semesters, list):
        raise HTTPException(status_code=500, detail="Invalid semesters data structure")

    if len(semesters) == 0:
        raise HTTPException(status_code=404, detail="No semesters found")

    total = len(semesters)

    index = total + sem_no if sem_no < 0 else sem_no - 1

    if index < 0 or index >= total:
        raise HTTPException(status_code=400, detail="Invalid semester number")

    semester = semesters[index]
    return SemesterCoursesResponse(status="success", data=semester, errors=[])
