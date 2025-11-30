import requests
import re
import json
from bs4 import BeautifulSoup
from core.utils import fetch_html, COURSE_CACHE_PREFIX, COURSE_TTL_HOURS
from typing import Optional
from core.cache import load_cache, save_cache, get_cache_metadata
from core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger("mydylms")


def get_course_contents(key: str, course_id: int):
    url = "https://mydy.dypatil.edu/rait/webservice/rest/server.php"
    params = {
        "wstoken": key,
        "wsfunction": "core_course_get_contents",
        "moodlewsrestformat": "json",
        "courseid": int(course_id),
    }

    try:
        response = requests.post(url, data=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as e:
        return {"status": "error", "error": str(e), "data": None}

    # Handle API errors
    if isinstance(data, dict) and "exception" in data:
        error_info = {
            "errorcode": data.get("errorcode"),
            "message": data.get("message"),
        }
        return {"status": "error", "error": error_info, "data": None}

    if not isinstance(data, list):
        return {
            "status": "invalid_response",
            "error": "Unexpected API response",
            "data": data,
        }

    # Parse course content
    formatted = []
    for section in data:
        if not isinstance(section, dict):
            continue
        week_name = section.get("name")
        week = {"week": week_name, "docs": []}
        for module in section.get("modules", []):
            modname = module.get("modname")
            doc_name_module = module.get("name")
            view_id = module.get("id")
            for content in module.get("contents", []):
                doc_url = content.get("fileurl")
                doc_id = None
                if doc_url and doc_url.startswith(
                    "https://mydy.dypatil.edu/rait/webservice/pluginfile.php"
                ):
                    match = re.search(r"pluginfile\.php/(\d+)/", doc_url)
                    if match:
                        doc_id = int(match.group(1))
                    doc_url = doc_url.replace("webservice/", "")
                    if doc_url.endswith("?forcedownload=1"):
                        doc_url = doc_url.replace("?forcedownload=1", "")

                week["docs"].append(
                    {
                        "view_id": view_id,
                        "doc_id": doc_id,
                        "module": doc_name_module,
                        "mod": modname,
                        "type": content.get("type"),
                        "doc_name": content.get("filename"),
                        "doc_size": content.get("filesize"),
                        "doc_url": doc_url,
                        "time": content.get("timemodified"),
                    }
                )
        formatted.append(week)

    return {"status": "success", "error": None, "data": formatted}


def get_course_contents_helper(key: str, course_id: int):
    cache_name = f"{COURSE_CACHE_PREFIX}{course_id}"
    cached = load_cache(cache_name, ttl_hours=COURSE_TTL_HOURS)
    metadata = get_cache_metadata(cache_name)

    if cached:
        if metadata:
            logger.info(
                f"Cache hit for course {course_id}. Age: {metadata['age_minutes']:.1f} min, TTL: {metadata['ttl_hours']}h"
            )
        else:
            logger.info(f"Cache hit for course {course_id} (metadata unavailable).")
        return cached

    logger.info(f"Cache miss for course {course_id}. Fetching fresh data...")
    course_data = get_course_contents(key, course_id)

    # NEW: handle error response properly
    if course_data.get("status") != "success":
        logger.warning(f"Error fetching course {course_id}: {course_data.get('error')}")
        return None

    data = course_data.get("data")
    if data:
        save_cache(cache_name, data, ttl_hours=COURSE_TTL_HOURS)
        logger.info(f"Saved fresh course {course_id} to cache.")
        return load_cache(cache_name, ttl_hours=COURSE_TTL_HOURS)

    logger.warning(f"No data returned for course {course_id}.")
    return None
