from pydantic import BaseModel, Field
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


class ValidateSessionResponse(BaseModel):
    success: bool = Field(
        ..., description="Indicates whether the validation was successful."
    )
    error: Optional[str] = Field(
        None, description="Error message if validation failed."
    )
    data: Optional[Dict[str, Any]] = Field(
        None, description="Contains validation result data."
    )
    status_code: int = Field(
        ..., description="HTTP-like status code returned by the core function."
    )
class LogoutResponseModel(BaseModel):
    success: bool = Field(
        ..., description="Indicates if the logout operation succeeded."
    )
    error: Optional[str] = Field(
        None, description="Error details if the logout failed."
    )
    data: Optional[Dict[str, Any]] = Field(
        None, description="Payload data, usually a message or status info."
    )
    status_code: int = Field(
        ..., description="HTTP status code representing the result."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "error": None,
                "data": {"message": "Logout successful and environment cleared."},
                "status_code": 200,
            }
        }
