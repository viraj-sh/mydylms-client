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
        status="success",
        data=MessageData(message="Unofficial mydylms API"),
        errors=[],
    )


@router.get(
    "/health",
    summary="Health check",
    response_model=HealthResponse,
    operation_id="check_system_health",
)
def health_check():
    return HealthResponse(
        status="success",
        data=HealthData(status="OK"),
        errors=[],
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    path = os.path.join(ASSETS_DIR, "favicon.ico")
    if not os.path.exists(path):
        import logging
        logging.warning(f"favicon not found: {path}")
    return FileResponse(path)