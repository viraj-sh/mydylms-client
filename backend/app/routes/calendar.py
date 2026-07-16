from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security
from app.schemas.calendar import CalendarBase
from app.services.calendar import calendar

router = APIRouter()


@router.get(
    "",
    response_model=list[CalendarBase],
    status_code=status.HTTP_200_OK,
    operation_id="get_calendar_events",
)
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
