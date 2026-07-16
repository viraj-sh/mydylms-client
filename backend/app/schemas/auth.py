from pydantic import BaseModel, Field
from typing import Optional


class LoginResponse(BaseModel):
    user_id: Optional[str] = Field(None)
    session_token: Optional[str] = Field(None)
    session_key: Optional[str] = Field(None)


class KeyResponse(BaseModel):
    web_service_key: Optional[str] = Field(None)
    features_service_key: Optional[str] = Field(None)
    service_key: Optional[str] = Field(None)
