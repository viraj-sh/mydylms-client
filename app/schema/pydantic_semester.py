from pydantic import BaseModel, Field
from typing import Optional, List, Any

class SubjectModel(BaseModel):
    id: int = Field(..., description="Unique identifier of the subject")
    name: str = Field(..., description="Name of the subject")


class SemesterModel(BaseModel):
    semester: str = Field(..., description="Name of the semester")
    subjects: List[SubjectModel] = Field(
        ..., description="List of subjects under this semester"
    )

class GetSemestersRequest(BaseModel):
    refetch: Optional[bool] = Field(
        False,
        description="If true, bypass cache and fetch fresh data from the Moodle server.",
    )

class GetSemestersResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the request was successful")
    error: Optional[str] = Field(None, description="Error message if any")
    data: Optional[List[SemesterModel]] = Field(
        None, description="List of semesters and subjects"
    )
    status_code: int = Field(..., description="HTTP status code of the response")
