from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.auth import login_helper, get_creds_helper, logout_helper
from core.info import get_user_profile_helper
from schema.pydantic_auth import (
    LoginData,
    LoginResponse,
    ProfileResponse,
    ProfileData,
    CredsData,
    CredsResponse,
    LogoutData,
    LogoutResponse,
    LoginRequest,
)
from dotenv import load_dotenv
from os import getenv
from core.utils import ENV_FILE

# load_dotenv(ENV_FILE)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login", summary="Login with email and password", response_model=LoginResponse
)
def login(request: LoginRequest):
    result = login_helper(request.email, request.password)
    if result["status"] != "success":
        raise HTTPException(status_code=401, detail=f"Login failed: {result['status']}")
    response_data = LoginData(
        status=result["status"],
        cookie=result.get("cookie"),
        sesskey=result.get("sesskey"),
        user_id=result.get("user_id"),
        semesters=result.get("semesters"),
    )
    return LoginResponse(status="success", data=response_data, errors=[])


@router.get("/me", summary="Get logged-in user profile", response_model=ProfileResponse)
def me():
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    user_id = getenv("USER_ID")
    if not token or not user_id:
        raise HTTPException(status_code=401, detail="User not logged in")

    profile = get_user_profile_helper(token, int(user_id))
    if not profile:
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")
    return ProfileResponse(status="success", data=profile, errors=[])


@router.get(
    "/creds", summary="Get current user credentials", response_model=CredsResponse
)
def creds():
    creds = get_creds_helper()
    return CredsResponse(status="success", data=creds, errors=[])


@router.delete("/logout", summary="Logout current user", response_model=LogoutResponse)
def logout():
    load_dotenv(ENV_FILE)
    token = getenv("TOKEN")
    sesskey = getenv("SESSKEY")
    if not token or not sesskey:
        raise HTTPException(status_code=401, detail="User not logged in")

    success = logout_helper(token, sesskey)
    if not success:
        raise HTTPException(status_code=500, detail="Logout failed")

    return LogoutResponse(status="success", data={"success": True}, errors=[])
