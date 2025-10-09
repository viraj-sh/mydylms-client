import requests
import re
import json
from bs4 import BeautifulSoup
from core.utils import fetch_html
from typing import Optional


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
