# Release Notes

No version tags, CHANGELOG file, or Git history were included with the uploaded project (only a source snapshot), so a traditional release history cannot be reconstructed. This document describes the **single snapshot state** of the codebase that was reverse-engineered.

## Current snapshot — "v1 (pre-release / development snapshot)"

**API version reported by the app**: `v1` (`settings.API_VERSION`), served under `/api/v1`.

### Implemented and working
- User registration, login, `me` endpoint (JWT-based, `app/api/user.py`).
- Loan CRUD (create, list by user, get by ID, delete).
- Financial analysis engine (EMI, ratios, health score, settlement % — `financial_engine.py`).
- Alternate DB-driven settlement prediction engine (`settlement_prediction.py`).
- AI-generated settlement recommendations and negotiation letters via Google Gemini, with automatic rule-based fallback.
- Settlement record creation, retrieval by user, retrieval by ID.
- Frontend: full page set (Login, Dashboard, Settlement Predictor, Negotiation Email, Know Your Rights, History) with client-side routing and protected routes.
- CORS-enabled API consumable from a Vite dev server.

### Known incomplete / not wired up (see Troubleshooting.md and Future_Improvements.md)
- Dashboard and History pages read from static alias endpoints, not real data.
- Negotiation letters are generated but never persisted to the `negotiation_letters` table.
- Two independent, non-reconciled settlement-scoring engines exist.
- Two independent, non-reconciled authentication implementations exist (only one is active).
- No automated tests, no CI/CD, no deployment tooling (Dockerfile, etc.).
- Hard-coded JWT secret; missing per-resource authorization checks; permissive CORS — not production-hardened.

### Environment / dependency versions observed
- Python 3.13, FastAPI 0.138.2, SQLAlchemy 2.0.51, Pydantic 2.13.4, `google-genai` 2.10.0 (Backend `requirements.txt`).
- React 19.2.7, React Router 7.18.1, Vite 8.1.0 (Frontend `package.json`).

For a prioritized backlog of what should happen before a "v1.0" public release, see [Future_Improvements.md](Future_Improvements.md).
