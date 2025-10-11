import re
import requests
from bs4 import BeautifulSoup
from core.utils import fetch_html, retry_session
import os
import json
from dotenv import load_dotenv
from os import getenv
from core.utils import ENV_FILE
from fastapi import HTTPException
import json
from urllib.parse import urlparse, unquote
import io, mimetypes
from fastapi.responses import StreamingResponse


def get_endlink(token, modtype, doc_id):
    url = f"https://mydy.dypatil.edu/rait/mod/{modtype}/view.php?id={doc_id}"
    html = fetch_html(url, token)
    if modtype == "flexpaper":
        m = re.search(
            r"PDFFile\s*:\s*'(https://mydy\.dypatil\.edu/rait/pluginfile\.php[^']+)'",
            html,
        )
        return m.group(1) if m else None
    soup = BeautifulSoup(html, "html.parser")
    if modtype == "dyquestion":
        c = soup.find("div", class_="dyquestioncontent")
        if c:
            for a in c.find_all("a", href=True):
                if "pluginfile.php" in a["href"]:
                    return a["href"]
            obj = c.find("object", attrs={"data": True})
            if obj and "pluginfile.php" in obj["data"]:
                return obj["data"]
        return None
    if modtype in ["presentation", "resource", "casestudy"]:
        divs = soup.find_all("div", class_=["presentationcontent"])
        for div in divs:
            obj = div.find("object", attrs={"data": True})
            if obj and "pluginfile.php" in obj["data"]:
                return obj["data"]
            for a in div.find_all("a", href=True):
                if "pluginfile.php" in a["href"]:
                    return a["href"]
        obj = soup.find("object", attrs={"data": True})
        if obj and "pluginfile.php" in obj["data"]:
            return obj["data"]
        for a in soup.find_all("a", href=True):
            if "pluginfile.php" in a["href"]:
                return a["href"]
        return None
    if modtype == "url":
        c = soup.find("div", class_="urlworkaround")
        if c:
            for a in c.find_all("a", href=True):
                if a["href"].startswith("https://"):
                    return a["href"]
        return None
    return None


def get_doc_details_by_view_id(view_id: int, data_dir: str = "data"):

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    course_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("course_") and f.endswith(".json")
    ]

    if not course_files:
        raise FileNotFoundError(f"No course_*.json files found in {data_dir}")

    for filename in course_files:
        file_path = os.path.join(data_dir, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                course_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue  # Skip unreadable or invalid files silently

        for week in course_data.get("data", []):
            for doc in week.get("docs", []):
                if doc.get("view_id") == view_id:
                    return doc

    return None


def _guess_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return ext


def _guess_media_type(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def _download_with_token(file_url: str) -> tuple[str, bytes]:
    load_dotenv(ENV_FILE)
    TOKEN = getenv("TOKEN")

    if not TOKEN:
        raise HTTPException(
            status_code=401, detail="Missing Moodle session token (TOKEN)"
        )

    parsed = urlparse(file_url)
    filename = unquote(os.path.basename(parsed.path)) or "downloaded_file"

    session = requests.Session()
    session.cookies.set("MoodleSession", TOKEN, domain=parsed.netloc)

    try:
        resp = session.get(file_url, stream=True, timeout=30)
        if not resp.ok:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Failed to fetch file from Moodle ({resp.status_code})",
            )
        return filename, resp.content
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Network error while fetching file: {e}"
        )


def _build_streaming_response(filename: str, content: bytes, inline: bool = True):
    """Return StreamingResponse for file view/download."""
    disposition = "inline" if inline else "attachment"
    mime = _guess_media_type(filename)
    return StreamingResponse(
        io.BytesIO(content),
        media_type=mime if inline else "application/octet-stream",
        headers={
            "Content-Disposition": f'{disposition}; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
