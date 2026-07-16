from pydantic import BaseModel, Field
from typing import Optional


class SubAttendance(BaseModel):
    classcode: Optional[str] = Field(None)
    totalclass: Optional[int] = Field(None)
    total_present: Optional[int] = Field(None)
    total_absent: Optional[int] = Field(None)
    presentage: Optional[float] = Field(None)
