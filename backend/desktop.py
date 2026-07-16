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
  <title>Uniclare</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap');
    body {
      margin: 0;
      padding: 0;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background-color: #111827;
      color: #ffffff;
      font-family: 'Poppins', system-ui, -apple-system, sans-serif;
    }
    h1 {
      font-size: 1.5rem;
      font-weight: 500;
      margin: 0;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <h1>Uniclare Client</h1>
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
    title="Uniclare Client",
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
