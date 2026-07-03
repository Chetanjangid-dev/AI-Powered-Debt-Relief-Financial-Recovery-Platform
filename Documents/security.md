# Security

This document lists security-relevant facts found directly in the code, plus assessment of their impact. Anything not explicitly labeled "Inferred" is drawn directly from source.

## Authentication & session

- **JWT signing key is hard-coded and committed to source**: `app/api/user.py` → `SECRET_KEY = "debt-relief-platform-secret-key-2024"`. Anyone with read access to the repository can forge valid tokens for any user (just needs an email to put in the `sub` claim — no server-side secret is actually secret). **Severity: Critical** if this code ever reaches a real deployment unmodified.
- **A second, different hard-coded secret** exists in the unused `DataBase/auth.py` (`"change-this-to-a-long-random-secret-key-in-production"`) — its own filler text is a direct warning that was never acted on.
- **Password hashing algorithm mismatch**: `requirements.txt` includes `passlib[bcrypt]`, but `app/api/user.py` explicitly avoids bcrypt — `pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")`, with the comment *"avoids bcrypt 5.0 compatibility issue."* `sha256_crypt` is a weaker, unsalted-by-default-work-factor scheme compared to bcrypt/argon2 for password storage (it's iterative but lacks bcrypt's memory-hardness). This looks like a pragmatic workaround for a dependency version conflict (`bcrypt==5.0.0` had breaking API changes affecting `passlib` in some versions) rather than a deliberate security choice.
- **No token refresh, no logout/blacklist mechanism**: tokens are valid for 60 minutes with no server-side revocation possible. Logging out (`AuthProvider.logout()`) only clears `localStorage` client-side; a stolen token remains valid until it expires naturally.
- **JWT stored in `localStorage`**: exposes the token to any XSS vulnerability (no `httpOnly` cookie used). No CSP headers are configured anywhere in the app.
- **`/api/v1/auth/me` and other protected-looking endpoints**: Actually, on inspection, **none of the loan/financial/settlement/ai routers require authentication at all** — `Depends(security)` (the `HTTPBearer` dependency) is used only in `GET /api/v1/auth/me`. Every other endpoint, including loan creation/deletion and settlement generation, accepts a raw `user_id`/`loan_id` in the request body with **no verification that the caller is actually that user**. Any authenticated (or even unauthenticated, since these endpoints don't check `Depends(security)` either) client can create, read, or delete any user's loan or settlement data by ID. **Severity: Critical** — this is an IDOR (Insecure Direct Object Reference) vulnerability across nearly the entire versioned API surface.

## CORS

`app/main.py`:
```python
allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
allow_credentials=True,
```
Including `"*"` in `allow_origins` together with `allow_credentials=True` is not just insecure — most browsers/CORS libraries will actually **reject** the wildcard when credentials are enabled (Starlette's `CORSMiddleware` will echo back the request's `Origin` verbatim when `"*"` is present with credentials, effectively allowing every origin). In practice this permits **any website** to make authenticated cross-origin requests against this API using a victim's stored token, if that token were somehow accessible to third-party JS (e.g., via XSS elsewhere).

## Input validation

- Pydantic + custom `validators.py` do a solid job of validating financial inputs (positive numbers, percentage ranges, income > expenses, balance ≤ loan amount) at the `financial_engine` layer.
- Database-layer validation is much thinner — e.g., `Loan.status` and `SettlementRecommendation.status` are free-text `String` columns with no CHECK constraint or enum, so any string can be written directly via SQLAlchemy if a code path bypasses the Pydantic schema.
- SQL injection risk is low: all queries go through SQLAlchemy's ORM query builder (`db.query(...).filter(...)`), no raw string-interpolated SQL was found, except `db_optimization.py`'s `conn.execute(text("ANALYZE"))`, which takes no user input and is safe.

## Secrets management

- No `.env` file is present in the uploaded project (only `.env.example` on the frontend) — `GEMINI_API_KEY` must be supplied by whoever deploys this. Good practice, assuming the JWT secret issue above is also fixed the same way.
- `Backend/debt_relief.db` (a real SQLite database file, potentially containing hashed passwords and financial data) is present in the uploaded project tree, suggesting it may have been committed to version control at some point. Database files should be `.gitignore`d — `Backend/.gitignore` was checked and does **not** currently exclude `*.db`.

## Rate limiting / abuse protection

None present anywhere — no rate limiting on login attempts (brute-force is possible), no rate limiting on AI-calling endpoints (a malicious or buggy client could rack up unbounded Gemini API costs), no CAPTCHA, no account lockout.

## Recommendations summary

1. Move JWT `SECRET_KEY` to an environment variable; generate a long random value per deployment; never commit it.
2. Fix CORS to an explicit allowlist of real frontend origins; drop `"*"`.
3. Add authorization checks: every endpoint that accepts a `user_id` or operates on a `loan_id`/`settlement_id` must verify the JWT's subject actually owns that resource, not just trust the body/path parameter.
4. Standardize on one password-hashing scheme (ideally bcrypt or argon2 via a maintained passlib/bcrypt version, or `argon2-cffi` directly) and delete the unused, inconsistent `DataBase/auth.py`.
5. Add login rate limiting / lockout.
6. Add per-user/IP rate limiting on the two AI-calling endpoints to control Gemini cost exposure.
7. Ensure `*.db` is gitignored and no real database file with user data is ever committed.
8. Add server-side token revocation (or move to short-lived tokens + refresh tokens) if session security matters for this product.
