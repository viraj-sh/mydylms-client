from typing import Annotated
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends

from app.core.http import HTTPClientDep, security


async def login(username: str, password: str, client: HTTPClientDep):

    data = {
        "uname_static": username,
        "username": username,
        "uname": username,
        "password": password,
    }
    return await client.post(
        url="https://mydy.dypatil.edu/rait/login/index.php",
        data=data,
        follow_redirects=True,
    )


async def keys(
    session_key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/user/managetoken.php",
        params={"sesskey": session_key},
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
