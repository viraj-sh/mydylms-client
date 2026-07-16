import socket
import threading
import time

import uvicorn
import webview
from app.core.config import settings
from app.main import app

HOST = settings.webview_host
PORT = settings.webview_port

SPLASH_HTML = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MYDY LMS</title>
    <style>
        html,
        body {
            margin: 0;
            width: 100%;
            height: 100%;
        }

        body {
            display: flex;
            align-items: center;
            justify-content: center;
            background: oklch(0.145 0 0);
            color: oklch(0.985 0 0);
            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        h1 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 500;
            line-height: 1.5;
            letter-spacing: 0;
            color: oklch(0.985 0 0);
        }
    </style>
</head>

<body>
    <h1>MYDY LMS</h1>
</body>

</html>
"""


def run_server() -> None:
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False,
        log_level="error",
    )


def navigate_when_ready(window: webview.Window) -> None:
    while True:
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                break
        except OSError:
            time.sleep(0.05)
    window.load_url(f"http://{HOST}:{PORT}")


def on_start(window: webview.Window) -> None:
    threading.Thread(target=navigate_when_ready, args=(window,), daemon=True).start()


threading.Thread(target=run_server, daemon=True).start()

window = webview.create_window(
    title="MYDY LMS",
    html=SPLASH_HTML,
    js_api=None,
    width=1200,
    height=800,
)

webview.start(
    func=on_start,
    args=(window,),
    private_mode=False,
    debug=False,
    icon="../.github/assets/icon.ico",
)
