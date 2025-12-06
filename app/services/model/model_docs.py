from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CourseDocument:
    view_id: int
    doc_id: Optional[int]
    module: Optional[str]
    mod: Optional[str]
    type: Optional[str]
    doc_name: Optional[str]
    doc_size: Optional[int]
    doc_url: Optional[str]
    time: Optional[int]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["CourseDocument"]:
        required = ["view_id", "doc_url"]
        if any(key not in data or data[key] is None for key in required):
            return None

        return cls(
            view_id=data.get("view_id"),
            doc_id=data.get("doc_id"),
            module=data.get("module"),
            mod=data.get("mod"),
            type=data.get("type"),
            doc_name=data.get("doc_name"),
            doc_size=data.get("doc_size"),
            doc_url=data.get("doc_url"),
            time=data.get("time"),
        )
