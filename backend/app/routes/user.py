from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
import re

from app.core.http import HTTPClientDep, security
from app.services.user import profile, keys
from app.schemas.user import KeyResponse, ProfileResponse

router = APIRouter()


@router.get("/keys", response_model=KeyResponse, status_code=status.HTTP_200_OK)
async def fetch_keys(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    session_key: str,
):
    try:
        response = await keys(session_key, token, client)
        if response.status_code == 200:
            key = re.findall(r"[a-fA-F0-9]{32}", response.text)
            key = (key + [None] * 3)[:3]
            if not any(key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No security keys found",
                )
            return KeyResponse(
                web_service_key=key[0],
                features_service_key=key[1],
                service_key=key[-1],
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No security keys found"
            )
    except HTTPException:
        raise


@router.get("/profile", status_code=status.HTTP_200_OK)
async def fetch_profile(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    try:
        response = await profile(user_id, token, client)
        if response.status_code == 200:
            return ProfileResponse(
                **dict(
                    zip(
                        ProfileResponse.model_fields.keys(),
                        re.findall(
                            r'<span\s+class=["\']profile_td2["\']>([^<]*)</span>',
                            response.text,
                        ),
                    )
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or unauthorized request",
            )
    except HTTPException:
        raise
