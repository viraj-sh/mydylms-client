from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Subject:
    id: int
    name: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["Subject"]:
        required_keys = {"id", "name"}
        if not all(key in data for key in required_keys):
            return None
        try:
            return cls(id=int(data["id"]), name=str(data["name"]))
        except (ValueError, TypeError):
            return None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Semester:
    semester: str
    subjects: List[Subject]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["Semester"]:
        if "semester" not in data or "subjects" not in data:
            return None

        try:
            subjects_list: List[Subject] = []
            for subj in data.get("subjects", []):
                parsed = Subject.from_json(subj)
                if parsed:
                    subjects_list.append(parsed)

            if not subjects_list:
                return None

            return cls(semester=str(data["semester"]), subjects=subjects_list)

        except Exception:
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "semester": self.semester,
            "subjects": [s.to_dict() for s in self.subjects],
        }
