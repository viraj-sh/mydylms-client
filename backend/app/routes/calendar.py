from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

from app.core.http import HTTPClientDep, security
from app.services.calendar import calendar
from app.schemas.calendar import CalendarBase

router = APIRouter()


@router.get("", response_model=list[CalendarBase], status_code=status.HTTP_200_OK)
async def fetch_annoucements(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await calendar(key, token, client)

        if response.status_code == 200:
            return response.json().get("events")
    except HTTPException:
        raise
