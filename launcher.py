import os
import sys
import uvicorn
import threading
import time
import socket
import argparse
import logging
import requests

# ------------------------------------------------------------
# PyInstaller base directory resolution
# ------------------------------------------------------------
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app_dir = os.path.join(base_dir, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.main import app
from app.core.utils import RESET, BOLD, FG_RED, FG_WHITE, FG_GREEN, FG_YELLOW


# ------------------------------------------------------------
# Argument parser (debug mode)
# ------------------------------------------------------------
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument("--debug", action="store_true")
parser.add_argument("--port", type=int, default=None)
args = parser.parse_args()


# ------------------------------------------------------------
# Find free port
# ------------------------------------------------------------
def find_free_port(start=8000, end=8100):
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port available")


# ------------------------------------------------------------
# Wait for server
# ------------------------------------------------------------
def wait_for_server(port, timeout=10):
    url = f"http://127.0.0.1:{port}/docs"
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.head(url, timeout=0.5)
            if r.status_code >= 200:
                return True
        except Exception:
            pass
        time.sleep(0.1)
    return False


# ------------------------------------------------------------
# Browser opener
# ------------------------------------------------------------
def open_browser(url):
    try:
        import webbrowser

        webbrowser.open(url, new=2)
    except Exception:
        pass


# ------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------
if __name__ == "__main__":

    # Determine port
    env_port = os.environ.get("PORT")
    port = args.port or (
        int(env_port) if env_port and env_port.isdigit() else find_free_port()
    )

    # ============================================================
    # DEBUG MODE
    # ============================================================
    if args.debug:
        print(
            f"""
{BOLD}{FG_RED}🚀 Starting application{RESET}
{FG_WHITE}• URL:{RESET} {BOLD}http://127.0.0.1:{port}{RESET}
{FG_WHITE}• Host:{RESET} 127.0.0.1
{FG_WHITE}• Port:{RESET} {BOLD}{port}{RESET}
{FG_WHITE}• Mode:{RESET} {BOLD}DEBUG{RESET}
{FG_WHITE}• Log level:{RESET} debug
"""
        )

        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="debug",
            reload=False,
        )
        sys.exit(0)

    # ============================================================
    # QUIET MODE
    # ============================================================
    print(
        f"""
{BOLD}{FG_RED}🚀 Starting application{RESET}
{FG_WHITE}• Mode:{RESET} {BOLD}QUIET{RESET}
"""
    )

    # Silence Uvicorn logs
    logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.access").disabled = True

    # Create Uvicorn server object
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="critical",
        access_log=False,
    )
    server = uvicorn.Server(config)

    # Run in background thread
    t = threading.Thread(target=server.run, daemon=True)
    t.start()

    # Wait for server startup
    if wait_for_server(port):
        url = f"http://127.0.0.1:{port}"
        print(
            f"""
{BOLD}{FG_GREEN}✅ Application is ready{RESET}
{FG_WHITE}• URL:{RESET} {BOLD}{url}{RESET}
{FG_WHITE}• Browser:{RESET} opening a new tab

{FG_YELLOW}Tip:{RESET} use --debug for full logs
{FG_YELLOW}GitHub:{RESET} https://github.com/viraj-sh/mydylms-client
{FG_YELLOW}Docs:{RESET}   https://github.com/viraj-sh/mydylms-client/wiki

{FG_RED}Note:{RESET} Keep this window open; closing it stops the server.
"""
        )

        open_browser(url)

    else:
        print(
            f"""
{BOLD}{FG_RED}❌ Application failed to start{RESET}
{FG_WHITE}• Port attempted:{RESET} {BOLD}{port}{RESET}
{FG_WHITE}• Mode:{RESET} QUIET (logs suppressed)

{FG_YELLOW}Troubleshooting:{RESET}
• Try: mydylms-client.exe --debug
• Check: port availability, app/main.py, uvicorn startup errors

"""
        )
        sys.exit(1)

    # Keep process alive
    try:
        while t.is_alive():
            time.sleep(0.2)
    except KeyboardInterrupt:
        server.should_exit = True
