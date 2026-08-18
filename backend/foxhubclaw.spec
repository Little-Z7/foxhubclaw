# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH).resolve().parents[1]
frontend_dist = root / "frontend" / "dist"

datas = []
if frontend_dist.is_dir():
    datas.append((str(frontend_dist), "frontend/dist"))

a = Analysis(
    ["foxhubclaw/desktop.py"],
    pathex=[str(Path(SPECPATH).resolve())],
    binaries=[],
    datas=datas,
    hiddenimports=["uvicorn.logging", "uvicorn.protocols.http.auto", "webview"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    upx=True,
    console=False,
)
