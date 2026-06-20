from pydantic import BaseModel, Field
from typing import Optional


class CalendarBase(BaseModel):
    id: Optional[int] = Field(None, validation_alias="id")
    event_title: Optional[str] = Field(None, validation_alias="name")
    date: Optional[int] = Field(None, validation_alias="timestart")
    created_at: Optional[int] = Field(None, validation_alias="timemodified")
