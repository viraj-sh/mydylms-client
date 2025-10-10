from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- Data Models ----------


class Subject(BaseModel):
    id: int = Field(..., description="Course ID in Moodle")
    name: str = Field(..., description="Course name")


class SemesterData(BaseModel):
    semester: str = Field(..., description="Semester name, e.g., 'Semester VI'")
    subjects: List[Subject] = Field(
        ..., description="List of subjects in this semester"
    )


class SemesterCoursesResponse(BaseModel):
    status: str = Field(
        ..., description="Status of the response, e.g., 'success' or 'error'"
    )
    data: SemesterData = Field(..., description="Courses within the selected semester")
    errors: List[str] = Field(
        default_factory=list, description="List of errors, if any"
    )


# ---------- Response Models ----------


class SemestersResponse(BaseModel):
    status: str = Field(
        ..., description="Status of the response, e.g., 'success' or 'error'"
    )
    data: List[SemesterData] = Field(..., description="List of available semesters")
    errors: List[str] = Field(
        default_factory=list, description="List of errors, if any"
    )
