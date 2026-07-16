from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security
from app.schemas.announcement import AnnouncementBase
from app.services.annoucements import annoucement, annoucement_all

router = APIRouter()


@router.get(
    "",
    response_model=list[AnnouncementBase],
    status_code=status.HTTP_200_OK,
    operation_id="fetch_latest_annoucements",
)
async def fetch_annoucements(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    user_id: str = Header(..., alias="x-user-id"),
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await annoucement(user_id, key, token, client)

        if response.status_code == 200:
            return response.json()
    except HTTPException:
        raise


@router.get(
    "/all",
    response_model=list[AnnouncementBase],
    status_code=status.HTTP_200_OK,
    operation_id="get_all_announcements",
)
async def fetch_all_annoucements(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    user_id: str = Header(..., alias="x-user-id"),
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await annoucement_all(user_id, key, token, client)

        if response.status_code == 200:
            return response.json()
    except HTTPException:
        raise
