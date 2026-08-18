# FoxHubClaw

Windows EXE and web desk for [RedFoxHub](https://redfox.hk) keyword search. Users paste their own RedFox API key, pick platforms, run live queries or daily/weekly jobs, then download Excel, HTML, and PDF reports.

This repository is mirrored to GitHub and Gitee.

## Modes

- **Desktop / internal:** no signup. Local SQLite. Launch the EXE or `scripts/run_desktop.ps1`.
- **Web product:** email or username + password. First registered user is admin and can enable or disable accounts.

## Requirements

- Python 3.12
- Node.js 20+
- A RedFox API key from https://redfox.hk

## Web (development)

```powershell
cd frontend
npm install
npm run build

cd ..\backend
python -m pip install -r requirements.txt
$env:FOXHUB_MODE="web"
python -m foxhubclaw.main --mode web --host 127.0.0.1 --port 8787
```

Open http://127.0.0.1:8787

Frontend hot reload:

```powershell
# terminal 1
cd backend
$env:FOXHUB_MODE="web"
python -m foxhubclaw.main --mode web

# terminal 2
cd frontend
npm run dev
```

Then open http://127.0.0.1:5173

## Desktop

```powershell
cd frontend
npm install
npm run build
cd ..\backend
$env:FOXHUB_MODE="desktop"
python -m foxhubclaw.desktop
```

Build a bundled EXE after the frontend build:

```powershell
cd backend
python -m pip install pyinstaller
pyinstaller foxhubclaw.spec
```

The artifact is `backend/dist/FoxHubClaw.exe`.

## Worker

Due jobs are also processed every minute while the server runs. To process once (for Task Scheduler):

```powershell
cd backend
python -m foxhubclaw.worker
```

## Tests

```powershell
cd backend
python -m pytest -v
```

## Platform coverage

Posts: Douyin, Xiaohongshu, WeChat, Bilibili, Toutiao, Kuaishou.

Comments: Kuaishou (search posts, then fetch comments on top results). Other platforms stay disabled until RedFox exposes a keyword comment API.

TikTok and Weibo appear in the catalog as unavailable.
