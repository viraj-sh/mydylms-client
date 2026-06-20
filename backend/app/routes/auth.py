import re
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated

from app.core.http import HTTPClientDep, security
from app.services.auth import login, logout
from app.schemas.auth import LoginResponse

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


@router.get("/logout", status_code=200)
async def auth_logout(
    session_key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    try:
        resposne = await logout(session_key, token, client)
        return resposne.text
    except Exception:
        raise
