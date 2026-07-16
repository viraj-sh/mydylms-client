from pydantic import BaseModel, Field
from typing import Optional


class AnnouncementBase(BaseModel):
    id: Optional[str] = Field(None, validation_alias="postid")
    title: Optional[str] = Field(None, validation_alias="subject")
    message: Optional[str] = Field(None, validation_alias="message")
    author: Optional[str] = Field(None, validation_alias="postuser_name")
    created_at: Optional[str] = Field(None, validation_alias="created_date")
