from pydantic import BaseModel, Field
from typing import List


class MessageData(BaseModel):
    message: str = Field(
        ..., description="A human-readable message describing the response"
    )


class MessageResponse(BaseModel):
    status: str = Field(
        ..., description="Status of the response, e.g., 'success' or 'error'"
    )
    data: MessageData = Field(..., description="Payload containing the response data")
    errors: List[str] = Field(
        default_factory=list, description="List of error messages if any"
    )


class HealthData(BaseModel):
    status: str = Field(..., description="Current health status of the system")


class HealthResponse(BaseModel):
    status: str = Field(
        ..., description="Status of the response, e.g., 'success' or 'error'"
    )
    data: HealthData = Field(..., description="Payload containing health information")
    errors: List[str] = Field(
        default_factory=list, description="List of error messages if any"
    )
