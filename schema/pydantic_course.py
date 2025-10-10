from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- Data Models ----------


class CourseDoc(BaseModel):
    view_id: Optional[int] = Field(None, description="View ID of the document")
    doc_id: Optional[int] = Field(
        None, description="Document ID (from pluginfile.php path)"
    )
    module: Optional[str] = Field(None, description="Module name (topic name)")
    mod: Optional[str] = Field(None, description="Module type (e.g., resource, assign)")
    type: Optional[str] = Field(None, description="File type (e.g., file, url)")
    doc_name: Optional[str] = Field(None, description="Document file name")
    doc_size: Optional[int] = Field(None, description="Document file size in bytes")
    doc_url: Optional[str] = Field(None, description="Public document URL")
    time: Optional[int] = Field(None, description="Unix timestamp when modified")


class CourseWeek(BaseModel):
    week: Optional[str] = Field(None, description="Section/week name")
    docs: List[CourseDoc] = Field(
        default_factory=list, description="List of documents in this section"
    )


# ---------- Response Models ----------


class CourseResponse(BaseModel):
    status: str = Field(
        ..., description="Status of the response, e.g., 'success' or 'error'"
    )
    data: List[CourseWeek] = Field(
        ..., description="Course content grouped by weeks/sections"
    )
    errors: List[str] = Field(
        default_factory=list, description="List of errors, if any"
    )
