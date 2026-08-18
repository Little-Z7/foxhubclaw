# FoxHubClaw Design

Date: 2026-08-18

## Product

FoxHubClaw is a keyword search desk for RedFoxHub social data. Users paste their own RedFox API key. The same UI ships as a Windows EXE (personal / internal) and a multi-user web product.

Brand name, window title, and installer filename are English. UI copy is Chinese.

## Runtime modes

- **desktop**: no signup. Local SQLite. Encrypted key on this machine. APScheduler while the app runs; `foxhubclaw-worker --once` plus Windows Task Scheduler when it does not.
- **web**: email or username + password. PostgreSQL in production, SQLite for local/dev. Per-user isolation. Admin can enable or disable accounts. First registered user is admin.

## Architecture

Monorepo: Python `core` + FastAPI `server` + Vue 3 frontend.

- Web deploy: FastAPI serves API and built static files.
- EXE: PyInstaller bundle starts FastAPI on localhost and opens WebView2 (`pywebview`).

## Query model

Platforms are declared in a capability table, not hardcoded in the UI.

Posts (keyword search): Douyin, Xiaohongshu, WeChat, Bilibili, Toutiao, Kuaishou.

Comments:

- Keyword comment APIs are used when RedFox exposes them.
- Kuaishou: search posts, then pull comments for the top N works (default 3).
- Platforms without a comment path stay grayed: Not supported.

TikTok and Weibo stay in the catalog as unavailable until a keyword post/comment path exists.

Unified result: `platform, kind, title, author, url, published_at, likes, comments, shares, extra`.

Partial success: failed platforms do not void the job.

## Reports

Each run writes `.xlsx` detail, HTML preview, and PDF summary. Files are viewed and downloaded in-app only. Keys never appear in logs, reports, or API responses (only last four characters in Settings).

## Security

- Passwords: bcrypt.
- Keys: Fernet. Desktop derives a machine-local secret; web uses `FOXHUB_SECRET_KEY`.
- JWT for web sessions.
- Admin cannot read raw keys.

## Errors and testing

Map RedFox auth, rate-limit, and network errors to Chinese messages on the run record. Core tests cover normalize, capability filter, crypto, and report files. API tests cover auth isolation and job create.
