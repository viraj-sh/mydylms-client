from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class AttendanceDataModel(BaseModel):
    attendance_value: Optional[str] = Field(
        None, description="Overall attendance percentage as a string"
    )


class AttendanceResponseModel(BaseModel):
    success: bool = Field(..., description="Indicates if the request was successful")
    error: Optional[str] = Field(None, description="Error message if any")
    data: Optional[AttendanceDataModel] = Field(
        None, description="Attendance data if request was successful"
    )
    status_code: int = Field(..., description="HTTP status code")



class AttendanceRecord(BaseModel):
    class_no: str = Field(..., description="Class number")
    subject: str = Field(..., description="Subject name")
    date: str = Field(..., description="Lecture date")
    time: str = Field(..., description="Lecture time")
    status: str = Field(..., description="Attendance status")


class AttendanceData(BaseModel):
    attendance: List[AttendanceRecord] = Field(
        default_factory=list, description="List of attendance entries"
    )


class CourseAttendanceResponse(BaseModel):
    success: bool = Field(..., description="Indicates success or failure")
    error: Optional[str] = Field(None, description="Error message if any")
    data: Optional[AttendanceData] = Field(None, description="Wrapped attendance data")
    status_code: int = Field(..., description="HTTP status code for the response")
