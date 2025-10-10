from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from schema.pydantic_semester import Subject, SemesterData
from api.semester import router
import pytest

# Setup FastAPI test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def mock_semesters_data():
    return [
        SemesterData(
            semester="Semester I",
            subjects=[
                Subject(id=1, name="Math"),
                Subject(id=2, name="Science"),
            ],
        ),
        SemesterData(
            semester="Semester II",
            subjects=[
                Subject(id=3, name="History"),
                Subject(id=4, name="Biology"),
            ],
        ),
    ]


# ---------- Tests for /sem ----------
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
    assert isinstance(data["data"], list)
    assert data["data"][0]["semester"] == "Semester I"
    assert data["data"][0]["subjects"][0]["name"] == "Math"


# ---------- Tests for /sem/{sem_no}/course ----------
@patch("api.semester.getenv", return_value="dummy_token")
@patch("api.semester.get_semesters_helper")
def test_get_courses_in_semester_success(
    mock_get_semesters, mock_getenv, mock_semesters_data
):
    mock_get_semesters.return_value = mock_semesters_data

    # Request first semester
    response = client.get("/sem/1/course")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["semester"] == "Semester I"
    assert len(data["data"]["subjects"]) == 2
    assert data["data"]["subjects"][0]["name"] == "Math"

    # Request last semester using negative index (-1)
    response = client.get("/sem/-1/course")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["semester"] == "Semester II"


@patch("api.semester.getenv", return_value="dummy_token")
@patch("api.semester.get_semesters_helper", return_value=[])
def test_get_courses_in_semester_empty(mock_get_semesters, mock_getenv):
    response = client.get("/sem/1/course")
    assert response.status_code == 404
