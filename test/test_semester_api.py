from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from schema.pydantic_course import CourseWeek, CourseDoc
from api.course import router
import pytest

# Setup FastAPI test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def mock_course_data():
    return [
        CourseWeek(
            week="Week 1",
            docs=[
                CourseDoc(doc_name="doc1.pdf"),
                CourseDoc(doc_name="doc2.pdf"),
            ],
        ),
        CourseWeek(
            week="Week 2",
            docs=[CourseDoc(doc_name="doc3.pdf")],
        ),
    ]


@patch("api.course.getenv")
@patch("api.course.get_course_contents_helper")
def test_get_course_contents_success(mock_get_course, mock_getenv, mock_course_data):
    mock_getenv.side_effect = lambda key: (
        "valid_key" if key in ["KEY_1", "KEY_2"] else None
    )
    mock_get_course.return_value = mock_course_data

    response = client.get("/course/7644/docs")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2
    assert data["data"][0]["week"] == "Week 1"
    assert data["data"][0]["docs"][0]["doc_name"] == "doc1.pdf"
