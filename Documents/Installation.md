# Installation

## Prerequisites

| Requirement | Version used in this repo | Notes |
|---|---|---|
| Python | 3.13 (per compiled `.pyc` files in `venv/`) | 3.10+ should work given the dependency versions |
| Node.js | Compatible with Vite 8 / React 19 | Node 20+ recommended |
| npm | bundled with Node | `package-lock.json` present, so `npm ci` is preferred |
| SQLite | none needed separately | bundled with Python's `sqlite3` module; SQLAlchemy talks to it directly |
| Google Gemini API key | optional | Only needed to enable real AI responses instead of the rule-based fallback |

## 1. Clone / extract the project

```bash
cd "AI Powered Debt Relief & Financial Recovery Platform"
```

## 2. Backend setup

```bash
cd Backend
python -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Environment variables

Create a `.env` file inside `Backend/` (this file is **not present** in the uploaded project and must be created manually):

```env
ENVIRONMENT=development
DATABASE_URL=sqlite:///../Database/debt_relief.db
GEMINI_API_KEY=your_gemini_api_key_here
```

> `GEMINI_API_KEY` is optional. If omitted, or if it's under 10 characters, the app automatically uses the rule-based fallback engine (`fallback_service.py`) for both the settlement recommendation and negotiation letter endpoints — the app will still function fully.

See [Configuration.md](Configuration.md) for what each variable actually does (including a discrepancy between `config.py`'s `DATABASE_URL` and what `DataBase/database.py` actually uses).

### Initialize the database (optional — happens automatically on startup too)

```bash
cd ../DataBase
python init_db.py
python db_optimization.py   # optional: adds indexes + runs ANALYZE
```

`Backend/app/main.py` also calls `init_database()` automatically on FastAPI startup (`Base.metadata.create_all`), so manual initialization is only needed if you want indexes applied via `db_optimization.py` ahead of time.

### Run the backend

```bash
cd ../Backend
uvicorn app.main:app --reload
```

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 3. Frontend setup

```bash
cd Frontend/vite-project
npm install
```

### Environment variables

Copy the example file:

```bash
cp .env.example .env
```

`.env.example` contents:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Run the frontend

```bash
npm run dev
```

Open `http://localhost:5173`.

## 4. Verify everything works

1. Visit `http://127.0.0.1:8000/api/v1/health/` — should return `{"status": "ok", ...}`.
2. Visit `http://localhost:5173/login` — register a new account.
3. You should be redirected to `/dashboard` after registering.

> **Known gap**: the Dashboard, History, and Know Your Rights pages call alias endpoints (`/api/dashboard`, `/api/history`, `/api/rights`) that return static/placeholder data regardless of what you enter — this is expected given the current code, not a setup error. See [Troubleshooting.md](Troubleshooting.md).

## 5. Build for production (frontend)

```bash
npm run build     # outputs to Frontend/vite-project/dist/
npm run preview   # serve the production build locally
```

There is no production build/process step defined for the backend beyond running Uvicorn directly (no Dockerfile, no gunicorn config present in the repo). See [Deployment.md](Deployment.md).
