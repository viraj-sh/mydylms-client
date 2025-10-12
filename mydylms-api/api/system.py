from fastapi import APIRouter
from schema.pydantic_system import (
    MessageResponse,
    MessageData,
    HealthResponse,
    HealthData,
)
from fastapi.responses import FileResponse

router = APIRouter(tags=["System"])  # All endpoints under "System" tag


@router.get("/", summary="Root endpoint", response_model=MessageResponse)
def home():
    return MessageResponse(
        status="success",
        data=MessageData(message="Unofficial mydylms API"),
        errors=[],
    )


@router.get("/health", summary="Health check", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="success",
        data=HealthData(status="OK"),
        errors=[],
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
