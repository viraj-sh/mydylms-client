from pydantic import BaseModel, Field
from typing import Optional


class SubjectDetail(BaseModel):
    id: Optional[int] = Field(None)
    sub_code: Optional[str] = Field(None, validation_alias="shortname")
    sub_title: Optional[str] = Field(None, validation_alias="fullname")
    instructor_name: Optional[str] = Field(None, validation_alias="instructorname")
    sem_title: Optional[str] = Field(None, validation_alias="planname")
    sem_period: Optional[str] = Field(None, validation_alias="semesterperiod")


class CourseDetail(BaseModel):
    id: Optional[int] = Field(None)
    sub_code: Optional[str] = Field(None, validation_alias="shortname")
    sub_title: Optional[str] = Field(None, validation_alias="fullname")
    enrolled_users: Optional[int] = Field(None, validation_alias="enrolledusercount")


class DocBase(BaseModel):
    doc_type: Optional[str] = Field(None, validation_alias="type")
    doc_title: Optional[str] = Field(None, validation_alias="filename")
    doc_size: Optional[int] = Field(None, validation_alias="filesize")
    doc_url: Optional[str] = Field(None, validation_alias="fileurl")
    teacher_name: Optional[str] = Field(None, validation_alias="author")
    created_at: Optional[int] = Field(None, validation_alias="timecreated")
    modified_at: Optional[int] = Field(None, validation_alias="timemodified")


class ModuleBase(BaseModel):
    module_id: Optional[int] = Field(None, validation_alias="id")
    module_title: Optional[str] = Field(None, validation_alias="name")
    module_type: Optional[str] = Field(None, validation_alias="modname")
    docs: list[DocBase] = Field(validation_alias="contents", default_factory=list)


class WeekBase(BaseModel):
    week_id: Optional[int] = Field(None, validation_alias="id")
    week_title: Optional[str] = Field(None, validation_alias="name")
    modules: list[ModuleBase] = Field(default_factory=list)
