from fastapi import APIRouter, HTTPException
from schema.pydantic_course import CourseResponse
from core.info import get_semesters_helper
from core.course import get_course_contents_helper
from dotenv import load_dotenv
from os import getenv
from core.utils import ENV_FILE

router = APIRouter(prefix="/course", tags=["Course"])


@router.get(
    "/{course_id}/docs", summary="Get course contents", response_model=CourseResponse
)
def get_course_contents(course_id: int):
    load_dotenv(ENV_FILE)
    key = getenv("KEY_1") or getenv("KEY_2")
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key (token)")

    try:
        course_data = get_course_contents_helper(key, course_id)
    except FileNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(
            status_code=404,
            detail=f"No cached data found for course {course_id}. Try fetching it first.",
        )
    except Exception as e:
        logger.exception("Unexpected error fetching course contents")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while fetching course contents: {str(e)}",
        )

    if not course_data:
        raise HTTPException(
            status_code=502, detail="Failed to fetch course contents from source"
        )

    return CourseResponse(status="success", data=course_data, errors=[])
