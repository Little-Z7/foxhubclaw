# FoxHubClaw Implementation Plan

> **For Claude:** Implement this plan in the current session. The user asked to finish the product without further confirmation gates.

**Goal:** Ship FoxHubClaw as a FastAPI + Vue 3 app that runs as a web service and as a Windows EXE with bundled dependencies.

**Architecture:** Shared Python core (RedFox adapters, normalize, reports, scheduler). FastAPI for both modes. Vue 3 SPA. Desktop wraps localhost + WebView2.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, SQLite/PostgreSQL, APScheduler, openpyxl, Jinja2, fpdf2, cryptography, passlib, PyJWT, pywebview, Vue 3, Vite, TypeScript.

---

### Task 1: Core domain tests and implementation

Files:

- `backend/tests/test_normalize.py`
- `backend/tests/test_capabilities.py`
- `backend/tests/test_crypto.py`
- `backend/tests/test_reports.py`
- `backend/foxhubclaw/normalize.py`
- `backend/foxhubclaw/capabilities.py`
- `backend/foxhubclaw/crypto.py`
- `backend/foxhubclaw/reports.py`

TDD the four modules, then implement.

### Task 2: RedFox adapters and query runner

Files:

- `backend/foxhubclaw/redfox_client.py`
- `backend/foxhubclaw/query_runner.py`
- `backend/tests/test_query_runner.py`

### Task 3: Database, auth, API

Files under `backend/foxhubclaw/api/` and `backend/foxhubclaw/models.py`.

### Task 4: Vue SPA

Files under `frontend/`.

### Task 5: Desktop launcher, scripts, README, verify, push
