from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import uvicorn
import webview

from foxhubclaw.api_app import app, mount_frontend
from foxhubclaw.config import settings


def choose_port(host: str, preferred: int) -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, preferred))
    except OSError:
        sock.bind((host, 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def resolve_icon() -> str | None:
    import sys

    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "frontend" / "public" / "favicon.ico")
    candidates.append(Path(__file__).resolve().parents[2] / "frontend" / "public" / "favicon.ico")
    for path in candidates:
        if path.is_file():
            return str(path)
    return None


def _serve() -> None:
    mount_frontend(app)
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="warning")


def main() -> None:
    settings.mode = "desktop"
    settings.port = choose_port(settings.host, settings.port)
    webview.settings["ALLOW_DOWNLOADS"] = True
    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    url = f"http://{settings.host}:{settings.port}/"
    for _ in range(50):
        time.sleep(0.1)
        try:
            import httpx

            if httpx.get(f"{url}api/meta", timeout=0.4).status_code == 200:
                break
        except Exception:
            continue
    icon = resolve_icon()
    window = webview.create_window(
        "FoxHubClaw",
        url,
        width=1280,
        height=840,
        min_size=(960, 640),
    )
    webview.start(icon=icon)


if __name__ == "__main__":
    main()
