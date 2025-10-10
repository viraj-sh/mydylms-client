from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest
from api.attendance import router

# --- Setup test app ---
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def mock_overall_attendance():
    return "85"  # overall attendance percentage


@pytest.fixture
def mock_courses_attendance():
    return [
        {
            "Subject": "Math",
            "Total Classes": 40,
            "Present": 34,
            "Absent": 6,
            "Percentage": 85.0,
            "altid": 101,
        },
        {
            "Subject": "Science",
            "Total Classes": 42,
            "Present": 39,
            "Absent": 3,
            "Percentage": 92.8,
            "altid": 102,
        },
    ]


@pytest.fixture
def mock_course_attendance():
    return [
        {
            "Class No": "1",
            "Subject": "Math",
            "Date": "2025-10-01",
            "Time": "10:00 AM",
            "Status": "Present",
        },
        {
            "Class No": "2",
            "Subject": "Math",
            "Date": "2025-10-02",
            "Time": "10:00 AM",
            "Status": "Absent",
        },
    ]


# ---------- Tests ----------


@patch("api.attendance.getenv", return_value="dummy_token")
@patch("api.attendance.get_overall_attendance_helper")
def test_get_overall_attendance_success(
    mock_helper, mock_getenv, mock_overall_attendance
):
    mock_helper.return_value = mock_overall_attendance

    response = client.get("/att")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"] == "85"


@patch("api.attendance.getenv", return_value=None)
def test_get_overall_attendance_not_logged_in(mock_getenv):
    response = client.get("/att")
    assert response.status_code == 401


@patch("api.attendance.getenv", return_value="dummy_token")
@patch("api.attendance.get_courses_attendance_helper")
def test_get_courses_attendance_success(
    mock_helper, mock_getenv, mock_courses_attendance
):
    mock_helper.return_value = mock_courses_attendance

    response = client.get("/att/courses")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    assert data["data"][0]["Subject"] == "Math"
    assert data["data"][1]["altid"] == 102


@patch("api.attendance.getenv", return_value="dummy_token")
@patch("api.attendance.get_courses_attendance_helper", return_value=None)
def test_get_courses_attendance_failure(mock_helper, mock_getenv):
    response = client.get("/att/courses")
    assert response.status_code == 500


@patch("api.attendance.getenv", return_value="dummy_token")
@patch("api.attendance.get_course_attendance_helper")
def test_get_course_attendance_success(
    mock_helper, mock_getenv, mock_course_attendance
):
    mock_helper.return_value = mock_course_attendance

    response = client.get("/att/course/101")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2
    assert data["data"][0]["Status"] == "Present"


@patch("api.attendance.getenv", return_value="dummy_token")
@patch("api.attendance.get_course_attendance_helper", return_value=None)
def test_get_course_attendance_failure(mock_helper, mock_getenv):
    response = client.get("/att/course/999")
    assert response.status_code == 500


@patch("api.attendance.getenv", return_value=None)
def test_get_course_attendance_not_logged_in(mock_getenv):
    response = client.get("/att/course/101")
    assert response.status_code == 401
