from pydantic import BaseModel
from typing import List, Optional


class LoginData(BaseModel):
    status: str
    cookie: Optional[str] = None
    sesskey: Optional[str] = None
    user_id: Optional[int] = None
    semesters: Optional[List[dict]] = None


class LoginResponse(BaseModel):
    status: str
    data: LoginData
    errors: List[str] = []


class ProfileData(BaseModel):
    mob_no: Optional[str]
    email_id: Optional[str]
    coll_name: Optional[str]
    degree_name: Optional[str]
    user_name: Optional[str]
    roll_no: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    country: Optional[str]
    religion: Optional[str]
    category: Optional[str]
    father_name: Optional[str]
    mother_name: Optional[str]
    pmob_no: Optional[str]
    femail_id: Optional[str]
    address: Optional[str]


class ProfileResponse(BaseModel):
    status: str
    data: ProfileData
    errors: List[str] = []


class KeysData(BaseModel):
    web_key: Optional[str]
    features_key: Optional[str]
    my_key: Optional[str]


class CredsData(BaseModel):
    token: Optional[str]
    sesskey: Optional[str]
    user_id: Optional[int]
    keys: KeysData


class CredsResponse(BaseModel):
    status: str
    data: CredsData
    errors: List[str] = []


class LogoutData(BaseModel):
    success: bool


class LogoutResponse(BaseModel):
    status: str
    data: LogoutData
    errors: List[str] = []


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenValidationData(BaseModel):
    valid: bool
    token: str | None = None


class TokenValidationResponse(BaseModel):
    status: str
    data: TokenValidationData
    errors: list[str]
