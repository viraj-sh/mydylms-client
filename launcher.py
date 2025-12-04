import os
import uvicorn
import ctypes
import sys
from app.core.utils import RESET, BOLD, FG_RED, FG_WHITE, FG_GREEN, FG_YELLOW

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

# ------------------------------
# ADD THIS SMALL BLOCK
# ------------------------------
import argparse

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--debug", action="store_true")
args, _ = parser.parse_known_args()
# ------------------------------


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    if args.debug:
        print(
            f"""
{BOLD}{FG_RED}🚀 Starting application{RESET}
{FG_WHITE}• URL:{RESET} {BOLD}http://127.0.0.1:{port}{RESET}
{FG_WHITE}• Host:{RESET} 127.0.0.1
{FG_WHITE}• Port:{RESET} {BOLD}{port}{RESET}
{FG_WHITE}• Mode:{RESET} {BOLD}DEBUG{RESET}
{FG_WHITE}• Reload:{RESET} enabled
{FG_WHITE}• Log level:{RESET} info
{FG_WHITE}• Access log:{RESET} enabled
        """
        )
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,  # safe inside PyInstaller
            log_level="debug",
        )
    else:
        print(f"Starting MYDYLMS API on http://127.0.0.1:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
