from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict


class CourseDocumentModel(BaseModel):

    view_id: int = Field(..., description="Unique view identifier")
    doc_id: Optional[int] = Field(
        None, description="Document id (may be null for external URLs)"
    )
    module: Optional[str] = Field(None, description="Module title/name")
    mod: Optional[str] = Field(
        None, description="Module type (e.g., resource, url, dyquestion)"
    )
    type: Optional[str] = Field(None, description="Type of entry: 'file'|'url' etc.")
    doc_name: Optional[str] = Field(None, description="Filename or display name")
    doc_size: Optional[int] = Field(None, description="Size in bytes")
    doc_url: Optional[str] = Field(None, description="Direct URL to the document")
    time: Optional[int] = Field(None, description="Unix timestamp when added")


class WeekDocsModel(BaseModel):

    week: Optional[str] = Field(None, description="Week name or grouping")
    docs: List[CourseDocumentModel] = Field(default_factory=list)


class StandardResponseModel(BaseModel):
    success: bool = Field(..., description="Whether the operation succeeded")
    error: Optional[Any] = Field(None, description="Error message or details (if any)")
    data: Optional[Any] = Field(
        None, description="Payload data (document metadata etc.)"
    )
    status_code: int = Field(..., description="HTTP status code to return")
