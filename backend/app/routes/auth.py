import re
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

from app.core.http import HTTPClientDep, security
from app.services.auth import login, keys
from app.schemas.auth import LoginResponse, KeyResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=201)
async def auth_login(username: str, password: str, client: HTTPClientDep):
    try:
        response = await login(username, password, client)
        if (
            "Invalid login, please try again" in response.text
            or "Academic Status" not in response.text
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid username or password",
            )
        elif "Academic Status" in response.text:
            user_id = (
                m.group(1)
                if (m := re.search(r"/user/profile\.php\?id=(\d+)", response.text))
                else None
            )
            sesskey = (
                m := re.search(r'sesskey["\'=:\s>]+([a-zA-Z0-9]{8,})', response.text)
            ) and m.group(1)

            return LoginResponse(
                user_id=user_id,
                session_token=client.cookies.get("MoodleSession"),
                session_key=sesskey,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid username or password",
            )
    except HTTPException:
        raise


@router.get("/keys", response_model=KeyResponse, status_code=status.HTTP_200_OK)
async def fetch_keys(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session_key: str,
    client: HTTPClientDep,
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
