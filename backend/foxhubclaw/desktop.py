from __future__ import annotations

import threading
import time
from pathlib import Path

import uvicorn
import webview

from foxhubclaw.api_app import app, mount_frontend
from foxhubclaw.config import settings


def _serve() -> None:
    mount_frontend(app)
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="warning")


def main() -> None:
    settings.mode = "desktop"
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
    icon = Path(__file__).resolve().parents[2] / "frontend" / "public" / "favicon.ico"
    window = webview.create_window(
        "FoxHubClaw",
        url,
        width=1280,
        height=840,
        min_size=(960, 640),
    )
    webview.start(icon=str(icon) if icon.exists() else None)


if __name__ == "__main__":
    main()
