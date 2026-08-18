from __future__ import annotations

import argparse

import uvicorn

from foxhubclaw.api_app import app, mount_frontend
from foxhubclaw.config import settings


def run_server() -> None:
    mount_frontend(app)
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


def main() -> None:
    parser = argparse.ArgumentParser(prog="FoxHubClaw")
    parser.add_argument("--mode", choices=["web", "desktop"], default=settings.mode)
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    args = parser.parse_args()
    settings.mode = args.mode
    settings.host = args.host
    settings.port = args.port
    run_server()


if __name__ == "__main__":
    main()
