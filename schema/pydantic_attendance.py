from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- Data Models ----------


class AttendanceCourse(BaseModel):
    Subject: str = Field(..., description="Course name")
    Total_Classes: Optional[int] = Field(None, alias="Total Classes")
    Present: Optional[int] = Field(None)
    Absent: Optional[int] = Field(None)
    Percentage: Optional[float] = Field(None)
    altid: Optional[int] = Field(None, description="Alternate attendance ID for course")


class AttendanceRecord(BaseModel):
    Class_No: str = Field(..., alias="Class No")
    Subject: str
    Date: str
    Time: str
    Status: str


# ---------- Response Models ----------


class OverallAttendanceResponse(BaseModel):
    status: str
    data: Optional[str] = Field(None, description="Overall attendance percentage")
    errors: List[str] = Field(default_factory=list)


class CoursesAttendanceResponse(BaseModel):
    status: str
    data: List[AttendanceCourse]
    errors: List[str] = Field(default_factory=list)


class CourseAttendanceResponse(BaseModel):
    status: str
    data: List[AttendanceRecord]
    errors: List[str] = Field(default_factory=list)
