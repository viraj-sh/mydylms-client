import re
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security
from app.schemas.user import KeyResponse, ProfileOldResponse, ProfileResponse
from app.services.user import keys, old_profile, profile

router = APIRouter()


@router.get("/v1/user/keys", response_model=KeyResponse, status_code=status.HTTP_200_OK)
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


@router.get(
    "/v0/user/profile",
    response_model=ProfileOldResponse,
    status_code=status.HTTP_200_OK,
)
async def fetch_profile_old(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    try:
        response = await old_profile(user_id, token, client)
        if response.status_code == 200:
            return ProfileOldResponse(
                **dict(
                    zip(
                        ProfileOldResponse.model_fields.keys(),
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


@router.get(
    "/v1/user/profile", response_model=ProfileResponse, status_code=status.HTTP_200_OK
)
async def fetch_profile(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
    key: str = Header(..., alias="X-API-Key"),
):
    try:
        response = await profile(user_id, key, token, client)
        if response.status_code == 200:
            if (
                isinstance(response.json(), dict)
                and response.json().get("exception") is not None
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"invalid or expired key -> {response.json().get('message')}",
                )
            return response.json()[-1]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or unauthorized request",
            )
    except HTTPException:
        raise
