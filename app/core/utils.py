import os
import json
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "assets"
)

ENV_FILE = Path(".env")
DATA_DIR = Path("data")
PROFILE_CACHE_NAME = "user_profile"
PROFILE_TTL_HOURS = 12

SEM_CACHE_NAME = "semesters"
SEM_TTL_HOURS = 6
COURSE_CACHE_PREFIX = "course_"
COURSE_TTL_HOURS = 1

OVERALL_TTL = 1  # hour
COURSES_TTL = 1  # hour
COURSE_TTL = 0.5  # 30 minutes

NON_DOWNLOADABLE_MODS = {"url"}
NON_VIEWABLE_MODS = {"url"}
FRONTEND_VIEWABLE_EXTENSIONS = {".pptx", ".docx"}
CHUNK_SIZE = 64 * 1024  # 64 KB, tune if desired


def dump_json(data, json_path: Path, indent: int = 4):
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_json(json_path):
    json_path = Path(json_path)
    if not json_path.exists():
        return None

    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def retry_session() -> requests.Session:
    retry_strategy = Retry(
        total=5,  # increased retries
        connect=5,  # retry connection errors
        read=5,  # retry read timeouts
        backoff_factor=1,  # exponential backoff: 1s, 2s, 4s...
        status_forcelist=[502, 503, 504, 408],
        allowed_methods=[
            "HEAD",
            "GET",
            "OPTIONS",
            "POST",
        ],  # explicitly allow POST retries
        raise_on_status=False,  # don't raise immediately, let requests handle it
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_html(url: str, token: str):
    session = requests.Session()
    session.cookies.set("MoodleSession", token)
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def frontend_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "static")
