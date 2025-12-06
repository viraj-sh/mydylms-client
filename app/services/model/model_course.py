from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class CourseDocument:
    view_id: int
    doc_id: Optional[int] = None
    module: Optional[str] = None
    mod: Optional[str] = None
    type: Optional[str] = None
    doc_name: Optional[str] = None
    doc_size: Optional[int] = None
    doc_url: Optional[str] = None
    time: Optional[int] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["CourseDocument"]:
        if not isinstance(data, dict) or "view_id" not in data:
            return None
        return cls(
            view_id=data["view_id"],
            doc_id=data.get("doc_id"),
            module=data.get("module"),
            mod=data.get("mod"),
            type=data.get("type"),
            doc_name=data.get("doc_name"),
            doc_size=data.get("doc_size"),
            doc_url=data.get("doc_url"),
            time=data.get("time"),
        )


@dataclass
class CourseSection:
    week: Optional[str]
    docs: List[CourseDocument] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["CourseSection"]:
        if not isinstance(data, dict):
            return None
        docs_data = data.get("docs", [])
        docs: List[CourseDocument] = []
        for doc in docs_data:
            parsed = CourseDocument.from_json(doc)
            if parsed:
                docs.append(parsed)
        return cls(week=data.get("week"), docs=docs)


@dataclass
class AttendanceRecord:
    class_no: str
    subject: str
    date: str
    time: str
    status: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["AttendanceRecord"]:
        required = ["Class No", "Subject", "Date", "Time", "Status"]
        for key in required:
            if key not in data or data[key] is None:
                return None
        return cls(
            class_no=data["Class No"],
            subject=data["Subject"],
            date=data["Date"],
            time=data["Time"],
            status=data["Status"],
        )
