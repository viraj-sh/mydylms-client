from typing import Annotated

import httpx
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security


async def login(username: str, password: str) -> tuple[httpx.Response, str | None]:
    data = {
        "uname_static": username,
        "username": username,
        "uname": username,
        "password": password,
    }
    async with httpx.AsyncClient(follow_redirects=True) as temp_client:
        response = await temp_client.post(
            url="https://mydy.dypatil.edu/rait/login/index.php",
            data=data,
        )
        moodle_session = temp_client.cookies.get("MoodleSession")
        return response, moodle_session


async def logout(
    session_key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/login/logout.php",
        params={"sesskey": session_key},
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
