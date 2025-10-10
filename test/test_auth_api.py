import pytest
from fastapi.testclient import TestClient
from main import app
import os
from dotenv import load_dotenv

client = TestClient(app)
ENV_FILE = os.path.join(os.path.dirname(__file__), "../.env")


@pytest.fixture(autouse=True)
def clear_env_before_each():
    for key in ["TOKEN", "USER_ID", "SESSKEY", "KEY_1", "KEY_2", "KEY_3"]:
        os.environ.pop(key, None)
    yield
    for key in ["TOKEN", "USER_ID", "SESSKEY", "KEY_1", "KEY_2", "KEY_3"]:
        os.environ.pop(key, None)
    if os.path.exists(ENV_FILE):
        os.remove(ENV_FILE)


def test_login_failure_invalid_creds(monkeypatch):
    def mock_login_helper(email, password):
        return {"status": "invalid"}

    monkeypatch.setattr("api.auth.login_helper", mock_login_helper)
    resp = client.post(
        "/auth/login", json={"email": "bad@example.com", "password": "wrong"}
    )
    assert resp.status_code == 401
    assert "Login failed" in resp.json()["detail"]


def test_login_success(monkeypatch):
    mock_result = {
        "status": "success",
        "cookie": "abc123",
        "sesskey": "sesskey123",
        "user_id": 1,
        "semesters": [{"id": 1}],
    }

    def mock_login_helper(email, password):
        return mock_result

    monkeypatch.setattr("api.auth.login_helper", mock_login_helper)
    resp = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "pass"}
    )
    data = resp.json()
    assert resp.status_code == 200
    assert data["status"] == "success"
    assert data["data"]["cookie"] == "abc123"


def test_me_not_logged_in(monkeypatch):
    def mock_get_user_profile_helper(token, user_id):
        return {"name": "test"}

    monkeypatch.setattr(
        "api.auth.get_user_profile_helper", mock_get_user_profile_helper
    )
    resp = client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "User not logged in"


def test_me_success(monkeypatch):
    os.environ["TOKEN"] = "abc"
    os.environ["USER_ID"] = "1"
    os.environ["SESSKEY"] = "sess123"

    def mock_get_user_profile_helper(token, user_id):
        return {
            "user_name": "John Doe",
            "email_id": "john@example.com",
            "mob_no": "1234567890",
            "coll_name": "Test College",
            "degree_name": "BSc",
            "roll_no": "001",
            "gender": "M",
            "dob": "2000-01-01",
            "postal_code": "123456",
            "city": "Test City",
            "country": "Test Country",
            "religion": "None",
            "category": "General",
            "father_name": "Father",
            "mother_name": "Mother",
            "pmob_no": "9876543210",
            "femail_id": "father@example.com",
            "address": "123 Test Street",
            "semesters": [{"id": 1}],
        }

    monkeypatch.setattr(
        "api.auth.get_user_profile_helper", mock_get_user_profile_helper
    )
    monkeypatch.setattr(
        "api.auth.get_creds_helper",
        lambda: {"token": "abc", "user_id": 1, "sesskey": "sess123"},
    )

    resp = client.get("/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["user_name"] == "John Doe"


def test_creds_success(monkeypatch):
    os.environ["TOKEN"] = "abc"
    os.environ["USER_ID"] = "1"
    os.environ["SESSKEY"] = "sess123"

    def mock_get_creds_helper():
        return {
            "token": "abc",
            "user_id": 1,
            "sesskey": "sess123",
            "keys": {
                "KEY_1": "key1",
                "KEY_2": "key2",
                "KEY_3": "key3",
            },
        }

    monkeypatch.setattr("core.auth.get_creds_helper", mock_get_creds_helper)
    resp = client.get("/auth/creds")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["token"] == "abc"


def test_logout_success(monkeypatch):
    os.environ["TOKEN"] = "abc"
    os.environ["SESSKEY"] = "sesskey"

    def mock_logout_helper(token, sesskey):
        return True

    monkeypatch.setattr("api.auth.logout_helper", mock_logout_helper)
    resp = client.delete("/auth/logout")
    data = resp.json()
    assert resp.status_code == 200
    assert data["status"] == "success"
    assert data["data"]["success"] is True


def test_logout_not_logged_in():
    resp = client.delete("/auth/logout")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "User not logged in"
