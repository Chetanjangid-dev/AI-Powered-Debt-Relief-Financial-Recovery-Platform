# Troubleshooting

This document catalogs real issues found while reading the code — things a developer extending this project will run into — not generic advice.

## "The Dashboard always shows zeros / placeholder data, no matter what loans I add"

**Cause**: `Dashboard.jsx` calls `GET /api/dashboard`, which is a hard-coded alias in `main.py`:
```python
@app.get("/api/dashboard")
async def alias_dashboard():
    return {"totalDebt": 0, ... "message": "Submit your loan details..."}
```
It never queries the database. If this call throws (e.g., network error), the frontend falls back to its own hard-coded `PLACEHOLDER_DATA` sample numbers instead — so either way, real data never appears.

**Fix**: Implement `alias_dashboard()` (or a new versioned endpoint) to actually query `crud.get_loans_by_user()` and `crud.get_financials_by_user()` for the logged-in user (extracted from the JWT), aggregate the numbers, and return them in the shape the frontend expects.

## "History page is always empty even after I generate a settlement"

**Cause**: `History.jsx` calls `GET /api/history`, another static alias that always returns `{"history": [], "items": [], "message": "Login to view..."}`. Meanwhile, `GET /api/v1/settlement/user/{user_id}` already exists and **does** query real settlement data — it's just not what the History page calls.

**Fix**: Point `History.jsx`'s API call at `/api/v1/settlement/user/{user_id}` (using the logged-in user's ID from `useAuth()`), or implement a real `/api/history` alias that does the same.

## "Know Your Rights content never changes / can't be edited"

**Cause**: `GET /api/rights` returns a Python literal hard-coded in `main.py`. There is no `rights` database table.

**Not necessarily a bug** — for a fixed, rarely-changing legal-reference page, static content may be an intentional simplification. Flagged here so it isn't mistaken for a data-loading bug.

## "I set GEMINI_API_KEY but the negotiation letter still uses generic placeholder text like '[Borrower Name]'"

Two possible causes:
1. The **fallback letter template** (`fallback_service._generate_letter`) always ends with literal `[Borrower Name]` / `[Contact Information]` / `[Date]` placeholders regardless of input — this is only used when Gemini is unreachable or the key is invalid/missing. Check `GET /api/v1/ai/status` and look for `gemini_error` in the response to confirm which path was used.
2. If calling the **alias** endpoint `/api/negotiation/generate` without a `borrower_name` field, it defaults to the literal string `"[Borrower Name]"` even when Gemini *is* used, because that's the field's default value in the request-body parsing logic.

## "Two different settlement percentages for what looks like the same borrower"

**Cause**: There are **two independent scoring engines** with different formulas:

| | `Backend/app/services/financial_engine.py` (+`calculator.py`) | `DataBase/settlement_prediction.py` |
|---|---|---|
| Used by | `/settlement/recommend`, `/financial/analyze`, both aliases | `/financial/predict-settlement/{user_id}` only |
| Health score formula | Weighted: EMI ratio (40) + expense ratio (30) + surplus (20) + overdue days (10) | Weighted differently: income-vs-expense savings ratio (40) + DTI (40) + debt-vs-annual-income (20) |
| Settlement % formula | Continuous: `60% ± surplus/overdue adjustments`, clamped 30–85% | Discrete tiers: 80/65/50/35/20% based on health-score bracket |
| Requires existing DB loan? | No — works from raw request body | Yes — requires active `Loan` rows already in DB for that user |

These are **not** the same algorithm and will produce different numbers for the same underlying borrower situation depending on which endpoint is called. **Inferred**: this looks like two different developers ("Backend" owner and "Khushi", per code comments) independently implementing the same feature without reconciling. Pick one canonical engine before extending either further.

## "sys.path hacks feel fragile — imports break depending on where I run things from"

Nearly every backend file that touches the database does something like:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "Database"))
import crud, schemas, models
```
Note the folder is capitalized `Database` in some path strings (e.g. `app/api/loan.py`, `app/api/financial.py`, `app/api/settlement.py`) but the actual folder on disk is `DataBase` (mixed case: `D`, `a`, `t`, `a`, `B`, `a`, `s`, `e`). On **case-insensitive filesystems** (default on Windows and macOS) this works by accident; **on case-sensitive filesystems (Linux, most CI/production containers) this import will fail** with `ModuleNotFoundError`.

**Fix**: rename all path references to the actual folder name `DataBase` consistently (or rename the folder to a fully-lowercase `database` and update every `sys.path.insert` accordingly — but audit for the naming collision with `Backend/app/core/database.py` and `DataBase/database.py` both named `database.py` first, see next item), and preferably replace the whole `sys.path` pattern with a proper installable local package (`pip install -e ../DataBase` with a `setup.py`/`pyproject.toml`) or by moving `DataBase/` inside `Backend/app/` as a regular subpackage.

## "Which debt_relief.db is actually being used?"

Two different `SQLALCHEMY_DATABASE_URL`s exist:
- `Backend/app/core/config.py`: `"sqlite:///../Database/debt_relief.db"` (defined but **not actually used** to build the engine — see [Configuration.md](Configuration.md))
- `DataBase/database.py`: `"sqlite:///./debt_relief.db"` (this **is** the one actually used, since `app/core/database.py` imports `engine` directly from `DataBase/database.py`)

Because the second URL is relative (`./debt_relief.db`), the actual file location depends on the **current working directory of the Python process**, not a fixed path. Running `uvicorn app.main:app` from `Backend/` vs. from the repo root vs. from `DataBase/` will each produce (or read from) a *different* SQLite file. This likely explains why a `debt_relief.db` file exists inside `Backend/` in the uploaded project — it was probably created by running the server from that directory.

**Fix**: use an absolute path (e.g., derived from `Path(__file__).resolve().parent`) for `SQLALCHEMY_DATABASE_URL`, and make `config.py`'s `DATABASE_URL` the actual single source of truth.

## "`Backend/app/core/security.py` is empty — where's the JWT logic?"

It lives directly inside `app/api/user.py` instead. `security.py` was likely scaffolded as intended structure but never filled in; JWT creation/verification, password hashing, and the `HTTPBearer` dependency were all implemented inline in the router file instead. Not a bug, but worth fixing for maintainability (see [Future_Improvements.md](Future_Improvements.md)).

## "google-genai import fails" / "ImportError: cannot import name 'genai' from 'google'"

`gemini_service.py` does a **local import** (`from google import genai`) inside the `try` block of `call_gemini()`, not a top-level import. If `google-genai` isn't installed, this raises `ImportError`, which is caught by the surrounding broad `except Exception`, and the app **silently falls back** rather than crashing — this is actually a deliberate resilience feature, not a bug, but it means a missing dependency can fail silently rather than being caught at startup. Run `pip install -r requirements.txt` fully, and check `GET /api/v1/ai/status` / server logs (`WARNING: Gemini API error: ...`) to confirm Gemini is actually active if you expect it to be.
