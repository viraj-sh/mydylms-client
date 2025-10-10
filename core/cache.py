import json
from pathlib import Path
from datetime import datetime, timedelta
from core.utils import DATA_DIR
import os

DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_cache(name: str, data: dict, ttl_hours: int = 6):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{name}.json"
    payload = {"timestamp": datetime.utcnow().isoformat(), "data": data}
    path.write_text(json.dumps(payload, indent=2))


def load_cache(name: str, ttl_hours: int = 6) -> dict | None:
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text())
        ts = datetime.fromisoformat(payload.get("timestamp"))
        if datetime.utcnow() - ts > timedelta(hours=ttl_hours):
            return None
        return payload.get("data")
    except Exception:
        return None


def clear_cache(name: str):
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        path.unlink()


def get_cache_metadata(cache_name: str) -> dict | None:
    cache_file = os.path.join(DATA_DIR, f"{cache_name}.json")
    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r") as f:
            data = json.load(f)

        timestamp_str = data.get("timestamp")
        if not timestamp_str:
            return None

        timestamp = datetime.fromisoformat(timestamp_str)
        age_seconds = (datetime.utcnow() - timestamp).total_seconds()
        age_minutes = age_seconds / 60

        # TTL can default to a fixed value if not stored in metadata
        ttl_hours = data.get("_metadata", {}).get("ttl_hours", 6)

        return {
            "timestamp": timestamp,
            "ttl_hours": ttl_hours,
            "age_seconds": age_seconds,
            "age_minutes": age_minutes,
        }
    except Exception:
        return None
