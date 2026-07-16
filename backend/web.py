import socket

import uvicorn
from app.main import app


def find_available_port(
    start_port: int, host: str = "127.0.0.1", max_tries: int = 50
) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(
        f"No free port found after {max_tries} tries starting at {start_port}"
    )


if __name__ == "__main__":
    port = find_available_port(8000)
    print(f"PORT={port}", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
