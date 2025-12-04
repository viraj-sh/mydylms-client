import os
import sys
import uvicorn
import threading
import time
import socket

# -------------------------------------------------------------------
# Minimal path setup for PyInstaller
# -------------------------------------------------------------------
if getattr(sys, "frozen", False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app_dir = os.path.join(base_dir, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.main import app


# -------------------------------------------------------------------
# Helper: wait for server
# -------------------------------------------------------------------
def wait_for_server(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.1)
    return False


# -------------------------------------------------------------------
# SKELETON MAIN LOGIC (Quiet only)
# -------------------------------------------------------------------
if __name__ == "__main__":

    port = 8000  # temporary hard-coded

    print(">>> Starting server (quiet mode)...")

    # silence uvicorn
    import logging

    logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.access").disabled = True

    # create uvicorn server object
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="critical",
        access_log=False,
    )
    server = uvicorn.Server(config)

    # run in thread
    t = threading.Thread(target=server.run, daemon=True)
    t.start()

    # wait until available
    if wait_for_server(port):
        print(">>> Server is ready on http://127.0.0.1:8000")
    else:
        print(">>> Server FAILED to start")
        sys.exit(1)

    # keep alive
    try:
        while t.is_alive():
            time.sleep(0.2)
    except KeyboardInterrupt:
        server.should_exit = True
