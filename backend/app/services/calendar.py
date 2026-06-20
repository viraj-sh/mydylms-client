from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Annotated

from app.core.http import HTTPClientDep, security


async def calendar(
    key: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/webservice/rest/server.php",
        params={
            "wstoken": key,
            "moodlewsrestformat": "json",
            "wsfunction": "core_calendar_get_calendar_events",
        },
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
