import logging
import logging.config
import os
from pythonjsonlogger import json


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Determine quiet mode
    QUIET_MODE = os.environ.get("QUIET", "1") == "1"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "json": {
                "()": "pythonjsonlogger.json.JsonFormatter",
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": (
                    "DEBUG" if not QUIET_MODE else "CRITICAL"
                ),
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": os.path.join(log_dir, "app.log"),
                "maxBytes": 5 * 1024 * 1024,  # 5MB per file
                "backupCount": 5,
                "level": (
                    "INFO" if not QUIET_MODE else "CRITICAL"
                ),  # suppress file if quiet
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO" if not QUIET_MODE else "CRITICAL",
        },
        "loggers": {
            "mydylms": {
                "handlers": ["console", "file"],
                "level": "DEBUG" if not QUIET_MODE else "CRITICAL",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
