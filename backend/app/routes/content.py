from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security
from app.schemas.content import (
    CourseDetail,
    SubjectDetail,
    WeekBase,
)
from app.services.content import course, docs, sem

router = APIRouter()


@router.get(
    "/current-course",
    response_model=list[SubjectDetail],
    status_code=status.HTTP_200_OK,
    operation_id="get_current_semester_courses",
)
async def fetch_current_semester_data(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    user_id: str = Header(..., alias="x-user-id"),
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await sem(key, user_id, token, client)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="unble to fetch semester data",
            )
    except Exception:
        raise


@router.get(
    "/course",
    response_model=list[CourseDetail],
    status_code=status.HTTP_200_OK,
    operation_id="get_enrolled_courses",
)
async def fetch_enrolled_courses(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    user_id: str = Header(..., alias="x-user-id"),
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await course(key, user_id, token, client)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="unble to fetch semester data",
            )
    except Exception:
        raise


@router.get(
    "/course/{course_id}",
    response_model=list[WeekBase],
    status_code=status.HTTP_200_OK,
    operation_id="get_course_docs",
)
async def fetch_course_docs(
    course_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await docs(key, course_id, token, client)
        if response.status_code == 200:
            if (
                isinstance(response.json(), dict)
                and response.json().get("exception") is not None
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"invalid or expired key -> {response.json().get('message')}",
                )
            return [WeekBase.model_validate(item) for item in response.json()]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="unble to fetch semester data",
            )
    except Exception:
        raise
