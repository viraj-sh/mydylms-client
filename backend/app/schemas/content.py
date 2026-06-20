from pydantic import BaseModel, Field
from typing import Optional


class SubjectDetail(BaseModel):
    id: Optional[int] = Field(None)
    sub_code: Optional[str] = Field(None, validation_alias="shortname")
    sub_title: Optional[str] = Field(None, validation_alias="fullname")
    instructor_name: Optional[str] = Field(None, validation_alias="instructorname")
    sem_title: Optional[str] = Field(None, validation_alias="planname")
    sem_period: Optional[str] = Field(None, validation_alias="semesterperiod")
