import os
import sys


def static_path() -> str:
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    elif os.path.basename(sys.executable).startswith("python"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    else:
        base_dir = os.path.dirname(sys.executable)
    return os.path.join(base_dir, "static")
