from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

from app.core.http import HTTPClientDep, security
from app.services.annoucements import annoucement, annoucement_all
from app.schemas.announcement import AnnouncementBase

router = APIRouter()


@router.get("", response_model=list[AnnouncementBase], status_code=status.HTTP_200_OK)
async def fetch_annoucements(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await annoucement(user_id, key, token, client)

        if response.status_code == 200:
            return response.json()
    except HTTPException:
        raise


@router.get(
    "/all", response_model=list[AnnouncementBase], status_code=status.HTTP_200_OK
)
async def fetch_all_annoucements(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await annoucement_all(user_id, key, token, client)

        if response.status_code == 200:
            return response.json()
    except HTTPException:
        raise
