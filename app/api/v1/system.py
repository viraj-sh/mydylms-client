from fastapi import APIRouter
from schema.pydantic_system import (
    MessageResponse,
    MessageData,
    HealthResponse,
    HealthData,
)
from fastapi.responses import FileResponse
from core.utils import ASSETS_DIR

router = APIRouter(tags=["System"])


@router.get(
    "/",
    summary="Root endpoint",
    response_model=MessageResponse,
    operation_id="get_system_info",
)
def home():
    return MessageResponse(
        success=True,
        data=MessageData(message="Unofficial mydylms API - v1"),
        error=None,
        status_code=200,
    )


@router.get(
    "/health",
    summary="Health check",
    response_model=HealthResponse,
    operation_id="check_system_health",
)
def health_check():
    return HealthResponse(
        success=True,
        data=HealthData(status="OK"),
        error=None,
        status_code=200,
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    print(os.path.join(ASSETS_DIR, "favicon.ico"))
    return FileResponse(os.path.join(ASSETS_DIR, "favicon.ico"))
