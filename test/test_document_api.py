import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

SAMPLE_DOC = {
    "view_id": 674089,
    "doc_id": 123,
    "module": "course",
    "mod": "resource",
    "type": "file",
    "doc_name": "sample.pdf",
    "doc_size": 1024,
    "doc_url": "https://example.com/sample.pdf",
    "time": 1234567890,
}


@pytest.fixture(autouse=True)
def mock_get_doc_details():
    with patch("api.document.get_doc_details_by_view_id", return_value=SAMPLE_DOC):
        yield


def test_metadata_returns_success():
    """Test /doc/{id} returns metadata correctly."""
    response = client.get("/doc/674089")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "doc_name" in data["data"]


def test_view_frontend_viewable():
    """Test action=view for pptx/docx returns frontend viewer info."""
    mock_doc = SAMPLE_DOC.copy()
    mock_doc["doc_name"] = "slides.pptx"
    with patch("api.document.get_doc_details_by_view_id", return_value=mock_doc):
        response = client.get("/doc/674089?action=view")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["viewer_type"] == "frontend"
        assert data["data"]["doc_name"] == "slides.pptx"


def test_view_non_viewable_redirect():
    """Test non-viewable mod (url) redirects."""
    mock_doc = SAMPLE_DOC.copy()
    mock_doc["mod"] = "url"
    with patch("api.document.get_doc_details_by_view_id", return_value=mock_doc):
        response = client.get("/doc/674089?action=view", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert "location" in response.headers


@patch("api.document._download_with_token")
def test_download_success(mock_download):
    """Test file download returns StreamingResponse."""
    mock_download.return_value = ("file.pdf", b"PDFDATA")
    response = client.get("/doc/674089?action=download")
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment")


def test_download_non_downloadable_redirect():
    """Test non-downloadable mod (url) redirects."""
    mock_doc = SAMPLE_DOC.copy()
    mock_doc["mod"] = "url"
    with patch("api.document.get_doc_details_by_view_id", return_value=mock_doc):
        response = client.get("/doc/674089?action=download", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert "location" in response.headers


def test_invalid_action():
    """Test invalid action returns 400."""
    response = client.get("/doc/674089?action=invalid")
    assert response.status_code == 400
    assert "Invalid action" in response.text


def test_not_found_document():
    """Test when helper returns None."""
    with patch("api.document.get_doc_details_by_view_id", return_value=None):
        response = client.get("/doc/999999")
        assert response.status_code == 404
        assert "not found" in response.text.lower()
