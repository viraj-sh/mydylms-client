from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, Dict


class LoginRequest(BaseModel):
    user_email: str = Field(..., description="User's Moodle email address")
    password: str = Field(
        ..., min_length=3, description="User's Moodle account password"
    )


class LoginData(BaseModel):
    user_id: int = Field(..., description="Unique Moodle user ID")
    sesskey: str = Field(..., description="Session security key")
    cookie: str = Field(..., description="Moodle session cookie")
    web_key: Optional[str] = Field(None, description="Web service security key")
    features_key: Optional[str] = Field(
        None, description="Features service security key"
    )
    my_key: Optional[str] = Field(None, description="Personalized service security key")


class StandardResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the operation succeeded")
    error: Optional[str] = Field(None, description="Error message if any")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data payload")
    status_code: int = Field(..., description="HTTP status code")
