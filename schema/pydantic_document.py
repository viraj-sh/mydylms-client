from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Any, Union


class DocumentData(BaseModel):
    view_id: int
    doc_id: Optional[int]
    module: str
    mod: str
    type: str
    doc_name: str
    doc_size: int
    doc_url: HttpUrl
    time: int


class FrontendViewerData(BaseModel):
    viewer_type: str
    doc_name: str
    mime_type: str
    doc_url: HttpUrl


class DocumentResponse(BaseModel):
    status: str
    data: Optional[Union[DocumentData, FrontendViewerData, Any]]
    errors: List[str]
