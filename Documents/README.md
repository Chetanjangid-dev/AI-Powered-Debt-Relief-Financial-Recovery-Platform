# AI Powered Debt Relief & Financial Recovery Platform

A full-stack web application that helps borrowers understand their debt situation, get an AI-generated settlement recommendation, and produce a professional negotiation letter to send to their lender.

Built with **React (Vite)** on the frontend, **FastAPI (Python)** on the backend, **SQLite + SQLAlchemy** for persistence, and **Google Gemini** for AI-generated negotiation content (with an automatic rule-based fallback when Gemini is unavailable).

> This documentation was produced by reverse-engineering the uploaded source code. Everything stated here is drawn directly from the code unless explicitly marked "**Inferred**" or "**Assumption**."

---

## 1. What the project does

A borrower who is behind on a loan can:

1. **Enter their loan and income details** and receive a financial-health analysis (EMI, EMI-to-income ratio, debt-to-income ratio, monthly surplus, "debt stress level") plus a recommended one-time settlement amount.
2. **Generate a negotiation letter** — a ready-to-send settlement request addressed to their lender, written by Gemini AI (or a rule-based fallback engine if no Gemini API key is configured).
3. **View a "Know Your Rights" page** with borrower-protection information (FDCPA, debt validation, statute of limitations, credit reporting, etc.) — currently static, hard-coded content.
4. **Track history** of past settlement/negotiation activity (endpoint exists but is not yet wired to persisted data — see [Troubleshooting](docs/Troubleshooting.md)).
5. **Log in / register** with email + password, protected by a JWT bearer token.

## 2. Problem it solves

Debt settlement negotiation is normally handled by expensive third-party debt-settlement companies or requires the borrower to understand collections law and financial math on their own. This platform automates the two hardest parts of that process:

- **The math** — objectively scoring how much financial stress a borrower is under and what settlement offer is realistic, using a EMI/DTI-based scoring engine (`financial_engine.py`, `settlement_prediction.py`).
- **The writing** — producing a professional, persuasive settlement letter tailored to the borrower's numbers, using generative AI with a deterministic fallback so the platform never fails to produce a letter.

## 3. Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router 7, Vite 8, plain CSS (no CSS framework) |
| Backend API | FastAPI 0.138, Uvicorn, Pydantic v2 |
| Database | SQLite (file-based), SQLAlchemy 2.0 ORM |
| Auth | JWT (`python-jose`) + password hashing (`passlib`) |
| AI | Google Gemini (`google-genai` SDK, model `gemini-2.0-flash-lite`) with a rule-based fallback service |

## 4. Repository layout

```
AI Powered Debt Relief & Financial Recovery Platform/
├── Backend/                 # FastAPI application
│   └── app/
│       ├── api/              # route modules (health, user, loan, financial, settlement, ai)
│       ├── core/              # config, database wiring, (empty) security module
│       ├── services/          # financial engine, calculator, Gemini + fallback AI services
│       └── utils/              # helpers, validators, custom exceptions
├── DataBase/                 # shared SQLAlchemy models/schemas + standalone teammate scripts
├── Frontend/vite-project/     # React SPA
├── Documents/docs.txt         # miscellaneous notes (not consumed by the app)
└── Readme.md                  # original project README
```

Full breakdown: [`docs/Folder_Structure.md`](docs/Folder_Structure.md)

## 5. Quick start

See [`docs/Installation.md`](docs/Installation.md) for full setup steps. Short version:

```bash
# Backend
cd Backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# create Backend/.env with GEMINI_API_KEY=... (optional — fallback works without it)
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd Frontend/vite-project
npm install
npm run dev
```

Backend runs at `http://127.0.0.1:8000` (Swagger docs at `/docs`). Frontend runs at `http://localhost:5173`.

## 6. Documentation index

| Document | Contents |
|---|---|
| [Architecture.md](docs/Architecture.md) | High-level system architecture and design rationale |
| [System_Design.md](docs/System_Design.md) | Component responsibilities, request lifecycle, sequence diagrams |
| [Folder_Structure.md](docs/Folder_Structure.md) | Annotated file tree |
| [Installation.md](docs/Installation.md) | Local setup, prerequisites, run commands |
| [Usage.md](docs/Usage.md) | How to use the app end-to-end (all 3 scenarios) |
| [Configuration.md](docs/Configuration.md) | Environment variables and settings |
| [API.md](docs/API.md) | Full REST API reference |
| [Database_Schema.md](docs/Database_Schema.md) | Tables, columns, relationships, ER diagram |
| [AI_Model.md](docs/AI_Model.md) | Gemini integration, prompt design, fallback logic |
| [Deployment.md](docs/Deployment.md) | How to deploy the backend and frontend |
| [Security.md](docs/Security.md) | Auth model, known weaknesses, recommendations |
| [Troubleshooting.md](docs/Troubleshooting.md) | Common issues found in the code and how to fix them |
| [Contributing.md](docs/Contributing.md) | Contribution guidelines |
| [Future_Improvements.md](docs/Future_Improvements.md) | Architect-level improvement backlog |
| [FAQ.md](docs/FAQ.md) | Frequently asked questions |
| [Glossary.md](docs/Glossary.md) | Domain and technical terms |
| [Screenshots.md](docs/Screenshots.md) | Reference to submitted UI screenshots |
| [Release_Notes.md](docs/Release_Notes.md) | Current version notes |

## 7. Key finding upfront (read this before extending the code)

This codebase shows clear signs of **parallel/independent team development that was never fully reconciled**:

- There are **two separate, inconsistent authentication implementations** — `DataBase/auth.py` (bcrypt-based, appears unused) and `Backend/app/api/user.py` (sha256_crypt-based, actually wired into the app).
- `Backend/app/main.py` contains a large block of **hard-coded "alias" endpoints** (`/api/auth/login`, `/api/settlement/predict`, `/api/rights`, etc.) that exist specifically to match a frontend teammate's ("Chetali's") exact expected field names, duplicating logic that already exists in the versioned routers under `/api/v1/...`.
- Two different settlement-scoring engines exist side by side: `Backend/app/services/financial_engine.py` (used by the versioned API) and `DataBase/settlement_prediction.py` (used only by one endpoint, `POST /api/v1/financial/predict-settlement/{user_id}`), with **different scoring formulas and different settlement-percentage outputs for the same input.**
- The frontend's dashboard, history, and rights pages are **not reading from the database at all** — they call hard-coded alias endpoints that return static or placeholder data regardless of what's stored.

These are documented in detail in [Troubleshooting.md](docs/Troubleshooting.md) and [Future_Improvements.md](docs/Future_Improvements.md) — read those before making changes, since "the API doesn't do what I expect" is very likely explained there.
