from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from schema.pydantic_semester import Subject, SemesterData, CourseDoc, CourseWeek
from api.semester import router
import pytest

# ✅ FIX: use a proper FastAPI app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def mock_semesters_data():
    return [
        SemesterData(
            semester="Semester 1",
            subjects=[
                Subject(id=1, name="Math"),
                Subject(id=2, name="Science"),
            ],
        ),
        SemesterData(
            semester="Semester 2",
            subjects=[
                Subject(id=3, name="History"),
                Subject(id=4, name="Biology"),
            ],
        ),
    ]


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
            docs=[
                CourseDoc(doc_name="doc3.pdf"),
            ],
        ),
    ]


@patch("api.semester.getenv", return_value="dummy_token")
@patch("api.semester.get_semesters_helper")
def test_get_all_semesters_success(
    mock_get_semesters, mock_getenv, mock_semesters_data
):
    mock_get_semesters.return_value = mock_semesters_data

    response = client.get("/sem/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"][0]["semester"] == "Semester 1"
    assert data["data"][0]["subjects"][0]["name"] == "Math"


@patch("api.semester.getenv")
@patch("api.semester.get_course_contents_helper")
def test_get_course_contents_success(mock_get_course, mock_getenv, mock_course_data):
    mock_getenv.side_effect = lambda key: (
        "valid_key" if key in ["KEY_1", "KEY_2"] else None
    )
    mock_get_course.return_value = mock_course_data

    response = client.get("/sem/7644/course")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"][0]["week"] == "Week 1"
    assert data["data"][0]["docs"][0]["doc_name"] == "doc1.pdf"
