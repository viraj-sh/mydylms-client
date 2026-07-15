from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security
from app.schemas.attendance import SubAttendance
from app.services.attendance import attendance

router = APIRouter()


@router.get(
    "",
    response_model=list[SubAttendance],
    status_code=status.HTTP_200_OK,
    operation_id="get_attendance",
)
async def fetch_attentdance(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    user_id: str = Header(..., alias="x-user-id"),
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await attendance(key, user_id, token, client)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="unble to fetch attendance",
            )
    except Exception:
        raise
