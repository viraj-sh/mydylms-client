from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated

from app.core.http import HTTPClientDep, security


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


async def profile(
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/local/users/profile.php",
        params={"id": user_id},
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
