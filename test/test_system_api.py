import os
import pytest
from fastapi.testclient import TestClient
from api.system import router
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_home():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["message"] == "Unofficial mydylms API"
    assert data["errors"] == []


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "OK"
    assert data["errors"] == []


def test_favicon():
    favicon_path = "static/favicon.ico"
    if not os.path.exists(favicon_path):
        os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
        with open(favicon_path, "wb") as f:
            f.write(b"")

    resp = client.get("/favicon.ico")
    assert resp.status_code == 200
    assert resp.headers["content-type"] in (
        "image/x-icon",
        "image/vnd.microsoft.icon",
        "application/octet-stream",
    )
