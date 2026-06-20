from fastapi import APIRouter, status, HTTPException, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated


from app.core.http import HTTPClientDep, security
from app.services.content import sem
from app.schemas.content import SubjectDetail

router = APIRouter()


@router.get(
    "/current-sem", response_model=list[SubjectDetail], status_code=status.HTTP_200_OK
)
async def fetch_current_semester_data(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
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
