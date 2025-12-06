from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class AttendanceData:
    attendance_value: Optional[str]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["AttendanceData"]:
        if "attendance_value" not in data:
            return None

        return cls(attendance_value=data.get("attendance_value"))


@dataclass
class AttendanceRecord:
    Subject: str
    Total_Classes: Optional[int] = None
    Present: Optional[int] = None
    Absent: Optional[int] = None
    Percentage: Optional[float] = None
    altid: Optional[int] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["AttendanceRecord"]:
        try:
            subject = data["Subject"]
            total = int(data["Total Classes"])
            present = int(data["Present"]) if data.get("Present") is not None else None
            absent = int(data["Absent"]) if data.get("Absent") is not None else None
            percentage = (
                float(data["Percentage"])
                if data.get("Percentage") is not None
                else None
            )
            altid = int(data["altid"]) if data.get("altid") is not None else None
            return cls(
                Subject=subject,
                Total_Classes=total,
                Present=present,
                Absent=absent,
                Percentage=percentage,
                altid=altid,
            )
        except (KeyError, ValueError, TypeError):
            return None


@dataclass
class CourseAttendanceRecord:
    class_no: str
    subject: str
    date: str
    time: str
    status: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["CourseAttendanceRecord"]:
        required = ["Class No", "Subject", "Date", "Time", "Status"]

        if not all(key in data and data[key] for key in required):
            return None

        return cls(
            class_no=data.get("Class No"),
            subject=data.get("Subject"),
            date=data.get("Date"),
            time=data.get("Time"),
            status=data.get("Status"),
        )
