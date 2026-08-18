# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

spec_dir = Path(SPECPATH).resolve()
root = spec_dir.parent
frontend_dist = root / "frontend" / "dist"
icon_file = root / "frontend" / "public" / "favicon.ico"

datas = []
binaries = []
hiddenimports = [
    "uvicorn.logging",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.loops.auto",
    "foxhubclaw",
    "foxhubclaw.api_app",
    "foxhubclaw.desktop",
    "webview",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
    "bcrypt",
    "jwt",
    "sqlalchemy.dialects.sqlite",
    "apscheduler.triggers.interval",
    "apscheduler.triggers.date",
    "apscheduler.jobstores.memory",
    "apscheduler.executors.pool",
]

if frontend_dist.is_dir():
    datas.append((str(frontend_dist), "frontend/dist"))
if icon_file.is_file():
    datas.append((str(icon_file), "frontend/public"))

# Do not collect_all(webview): it pulls optional Qt backends into a huge EXE.
for package in ("uvicorn", "fastapi", "sqlalchemy", "cryptography"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

hiddenimports += collect_submodules("foxhubclaw")

a = Analysis(
    ["foxhubclaw/desktop.py"],
    pathex=[str(spec_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt5", "PyQt6", "PySide2", "PySide6", "gi", "gtk"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FoxHubClaw",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(icon_file) if icon_file.is_file() else None,
)
