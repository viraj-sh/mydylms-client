# models/course_models.py
from pydantic import BaseModel, Field
from typing import Optional, Any, List


class CourseDocumentModel(BaseModel):
    view_id: Optional[int] = Field(None, description="Internal view id for the module")
    doc_id: Optional[int] = Field(
        None, description="Parsed document id from pluginfile url if available"
    )
    module: Optional[str] = Field(None, description="Module name (display name)")
    mod: Optional[str] = Field(
        None, description="Module type (e.g., resource, url, file)"
    )
    type: Optional[str] = Field(
        None, description="Content type (from Moodle content item)"
    )
    doc_name: Optional[str] = Field(None, description="Filename or document name")
    doc_size: Optional[int] = Field(None, description="File size in bytes if provided")
    doc_url: Optional[str] = Field(None, description="Public URL to fetch the document")
    time: Optional[int] = Field(
        None, description="Unix timestamp when content was modified"
    )


class CourseSectionModel(BaseModel):
    week: Optional[str] = Field(None, description="Section name (e.g., Week 1)")
    docs: List[CourseDocumentModel] = Field(
        default_factory=list, description="List of documents in this section"
    )


class CourseDocsRequestModel(BaseModel):
    course_id: int = Field(..., ge=1, description="Numeric Moodle course id")
    refetch: Optional[bool] = Field(
        False, description="If true, bypass cached request and refetch from Moodle"
    )


class StandardResponseModel(BaseModel):
    success: bool = Field(..., description="Whether the operation succeeded")
    error: Optional[Any] = Field(None, description="Error information or message")
    data: Optional[Any] = Field(
        None,
        description="Payload. For this endpoint: List[CourseSectionModel] on success",
    )
    status_code: int = Field(
        ..., description="HTTP status code to be used for the response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "error": None,
                "data": [
                    {
                        "week": "Week 1",
                        "docs": [
                            {
                                "view_id": 123,
                                "doc_id": 456,
                                "module": "Lecture notes",
                                "mod": "resource",
                                "type": "file",
                                "doc_name": "intro.pdf",
                                "doc_size": 12345,
                                "doc_url": "https://example.com/pluginfile.php/456/...",
                                "time": 1699999999,
                            }
                        ],
                    }
                ],
                "status_code": 200,
            }
        }
