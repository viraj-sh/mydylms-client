from pydantic import BaseModel, Field
from typing import Optional


class KeyResponse(BaseModel):
    web_service_key: Optional[str] = Field(None)
    features_service_key: Optional[str] = Field(None)
    service_key: Optional[str] = Field(None)


class ProfileResponse(BaseModel):
    user_name: Optional[str] = Field(None)
    roll_no: Optional[str] = Field(None)
    gender: Optional[str] = Field(None)
    dob: Optional[str] = Field(None)
    postal_code: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    country: Optional[str] = Field(None)
    religion: Optional[str] = Field(None)
    category: Optional[str] = Field(None)
    father_name: Optional[str] = Field(None)
    mother_name: Optional[str] = Field(None)
    pmob_no: Optional[str] = Field(None)
    femail_id: Optional[str] = Field(None)
    address: Optional[str] = Field(None)
