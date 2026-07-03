# Future Improvements

Architect-level review of the codebase, organized by category. Each item notes the concrete evidence found in the code.

## Architecture & maintainability

1. **Eliminate the `sys.path.insert` integration pattern.** Nearly every router file (`app/api/loan.py`, `financial.py`, `settlement.py`, `user.py`, plus `core/database.py`, `services/gemini_service.py`) manually inserts `DataBase/` into `sys.path` to import `crud`, `models`, `schemas`. This is fragile (breaks on case-sensitive filesystems — see [Troubleshooting.md](Troubleshooting.md)), makes imports order-dependent, and hides a real dependency behind indirection. **Recommendation**: move `DataBase/` inside `Backend/app/` as a proper subpackage (`app/db/`), or turn it into an installable local package with a `pyproject.toml` and `pip install -e`.
2. **Reconcile the two settlement-scoring engines.** `financial_engine.py`/`calculator.py` and `settlement_prediction.py` implement different formulas for financial health score and settlement percentage (see [Troubleshooting.md](Troubleshooting.md) for the side-by-side comparison). Having two "sources of truth" for the same business concept is a correctness risk. **Recommendation**: pick one, deprecate the other, or explicitly document why both exist (e.g., one is "quick estimate," the other is "DB-verified", and make that distinction visible in the API and UI).
3. **Reconcile the two authentication implementations.** `app/api/user.py` (sha256_crypt, actually used) and `DataBase/auth.py` (bcrypt, unused) duplicate the same responsibility. Delete the unused one, or make it the single source of truth used by `app/api/user.py` instead of reimplementing inline.
4. **Remove or clearly label the `main.py` alias endpoints.** The block of `/api/auth/*`, `/api/dashboard`, `/api/settlement/predict`, `/api/negotiation/generate`, `/api/rights`, `/api/history` endpoints exists solely to match one frontend implementation's expectations, duplicating and in some cases diverging from the versioned `/api/v1/...` routes. **Recommendation**: either update the frontend to call the versioned API directly (removing the need for aliases) or formally adopt the alias paths as the real public API and delete the "duplicate" versioned routes that overlap — maintaining both permanently doubles the maintenance surface for every future change.
5. **`app/core/security.py` is empty.** Move the JWT/password logic currently embedded in `app/api/user.py` into it, matching the apparent original intent of the file structure.
6. **Fix the `DATABASE_URL` / hard-coded SQLite path mismatch** (see [Configuration.md](Configuration.md) and [Troubleshooting.md](Troubleshooting.md)) — make `config.py`'s `DATABASE_URL` the actual value used to construct the SQLAlchemy engine, and use an absolute path.

## Data model

7. **Wire `negotiation_letters` table into the actual flow.** `crud.save_negotiation_letter()` exists but no router calls it — generated letters are returned to the client and then lost; they cannot be retrieved later via `GET /api/v1/settlement/{id}`.
8. **Add DB-level constraints** for `status` columns (`loans.status`, `settlement_recommendations.status`) — currently free-text strings with no CHECK constraint or native enum, relying entirely on application-layer discipline.
9. **Use `Decimal`/fixed-point storage for money fields** instead of `Float`, to avoid floating-point rounding drift accumulating across settlement calculations.
10. **Apply `db_optimization.py`'s indexes automatically** as part of `init_database()` (or via a proper migration tool — see next point) rather than requiring a manually-run separate script.
11. **Adopt a real migration tool (Alembic).** Currently schema changes require manually re-running `Base.metadata.create_all`, which does not alter existing tables — there is no migration path for schema evolution once real data exists.

## API design

12. **Enforce resource ownership.** Nearly every endpoint accepting a `user_id`/`loan_id` trusts it blindly rather than deriving it from the authenticated JWT — see [Security.md](Security.md) for the severity assessment.
13. **Standardize request bodies vs. query params.** `POST /financial/predict-settlement/{user_id}` uses query parameters for `monthly_income`/`monthly_expenses` while every other POST endpoint uses a JSON body — inconsistent and easy to misuse.
14. **Add pagination** to list endpoints (`GET /loans/user/{id}`, `GET /settlement/user/{id}`, `GET /financial/monthly/{id}`) — currently return unbounded result sets.
15. **Version the alias endpoints or remove them** — see item 4.

## AI integration

16. **Use Gemini's native structured output / JSON mode** instead of prompt-instructed JSON + manual `json.loads()` + markdown-fence stripping — more reliable, fewer silent-fallback triggers from parse failures.
17. **Add retry-with-backoff** before falling back (the `tenacity` dependency is already installed but unused).
18. **Add per-user/IP rate limiting** on AI-calling endpoints to bound Gemini API cost exposure (see [Security.md](Security.md)).
19. **Log/metric which path was used** (`gemini` vs `fallback`) in a structured, queryable way — today it's only a `print()` statement, invisible outside local console output.
20. **Personalize the fallback letter** with actual borrower/lender names (currently hard-codes `[Borrower Name]` placeholders even when those values were supplied — see [Troubleshooting.md](Troubleshooting.md)).

## Testing

21. **No automated tests exist anywhere in the repository** — no `pytest`, no `vitest`/`jest`, no `tests/` directory on either side. Recommended priority order: (a) unit tests for `calculator.py`/`financial_engine.py` (pure functions, highest ROI), (b) integration tests for the auth flow, (c) contract tests confirming alias endpoints and versioned endpoints stay in sync where they're supposed to overlap.

## Observability

22. **No structured logging, no error tracking (Sentry etc.), no request tracing.** All diagnostic output is `print()` statements (e.g., in `gemini_service.py`, `main.py`'s startup handler). Recommend Python's standard `logging` module at minimum, with log levels, before any real deployment.

## Frontend

23. **Wire Dashboard, History, and (optionally) Know Your Rights to real backend data** instead of static/placeholder responses (see [Troubleshooting.md](Troubleshooting.md)).
24. **Centralize error handling in `api.js`** — currently every page's `catch` block handles failures independently and inconsistently (some fall back to placeholder data, some show an error string, some do neither).
25. **No accessibility audit artifacts found** (no `aria-*` usage spotted in the reviewed components beyond default HTML semantics) — worth a pass given this product serves a financially-stressed, potentially vulnerable user base.
