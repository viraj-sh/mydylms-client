from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated

from app.core.http import HTTPClientDep, security


async def annoucement(
    user_id: str,
    key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/webservice/rest/server.php",
        params={
            "wstoken": key,
            "moodlewsrestformat": "json",
            "wsfunction": "local_user_announcements_custom",
            "userid": user_id,
        },
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )


async def annoucement_all(
    user_id: str,
    key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/webservice/rest/server.php",
        params={
            "wstoken": key,
            "moodlewsrestformat": "json",
            "wsfunction": "local_user_announcementsall_custom",
            "userid": user_id,
        },
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
