from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class UserProfile:
    user_name: str
    roll_no: str
    mob_no: Optional[str] = None
    email_id: Optional[str] = None
    coll_name: Optional[str] = None
    degree_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    religion: Optional[str] = None
    category: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    pmob_no: Optional[str] = None
    femail_id: Optional[str] = None
    address: Optional[str] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Optional["UserProfile"]:
        required = ["user_name", "roll_no"]
        if not all(k in data and data[k] for k in required):
            return None
        return cls(**{field: data.get(field) for field in cls.__dataclass_fields__})
