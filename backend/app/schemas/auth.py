from pydantic import BaseModel
from typing import Optional


class LoginResponse(BaseModel):
    user_id: Optional[str]
    session_token: Optional[str]
    session_key: Optional[str]
