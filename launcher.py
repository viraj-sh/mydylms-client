import os
import uvicorn
import ctypes
import sys

if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(base_dir, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.main import app


def enable_vt100():
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


os.environ["NO_COLOR"] = "1"
os.environ["UVICORN_NO_COLOR"] = "1"

enable_vt100()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting MYDYLMS API on http://127.0.0.1:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
