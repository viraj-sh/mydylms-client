from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.http import HTTPClientDep, security


async def attendance(
    key: str,
    user_id: str,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    client: HTTPClientDep,
):
    return await client.get(
        url="https://mydy.dypatil.edu/rait/webservice/rest/server.php",
        params={
            "wstoken": key,
            "moodlewsrestformat": "json",
            "wsfunction": "local_user_attendence_custom",
            "userid": user_id,
        },
        headers={"Cookie": f"MoodleSession={token.credentials}"},
    )
