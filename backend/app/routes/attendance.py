from fastapi import APIRouter, status, HTTPException, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated


from app.core.http import HTTPClientDep, security
from app.services.attendance import attendance
from app.schemas.attendance import SubAttendance

router = APIRouter()


@router.get("", response_model=list[SubAttendance], status_code=status.HTTP_200_OK)
async def fetch_attentdance(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
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
