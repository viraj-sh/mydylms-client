from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any

from core.utils import standard_response
from core.logging import setup_logging
from core.exceptions import handle_exception
from services.auth import login
from schema.pydantic_auth import LoginRequest, StandardResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    response_model=StandardResponse,
    operation_id="login_user",
)
async def login_user(
    payload: LoginRequest = Body(..., description="Moodle user credentials")
) -> JSONResponse:
    logger = setup_logging(name="auth_router.login", level="INFO")
    try:
        logger.info(f"[AuthAPI] Login attempt for user: {payload.user_email}")
        result: Dict[str, Any] = login(
            user_email=payload.user_email, password=payload.password
        )

        # Ensure valid response structure
        if not isinstance(result, dict) or "status_code" not in result:
            logger.warning("[AuthAPI] Unexpected return format from core.login()")
            result = standard_response(
                False, error="Internal response format error", status_code=500
            )

        return JSONResponse(content=result, status_code=result.get("status_code", 200))

    except Exception as exc:
        logger.exception("[AuthAPI] Exception occurred during login")
        error_response = handle_exception(logger, exc, context="login_user")
        return JSONResponse(
            content=error_response, status_code=error_response.get("status_code", 500)
        )
