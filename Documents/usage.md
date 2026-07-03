# Usage Guide

This walks through the app the way an end user experiences it, referencing the actual pages and endpoints they trigger.

## 1. Register / Sign in

- Navigate to `/login`.
- Toggle between **Sign In** and **Create Account** using the link at the bottom of the card (`Login.jsx`, `isRegister` state).
- Registration requires: full name, email, password (min 6 characters, enforced by `RegisterRequest` Pydantic schema in `app/api/user.py`), and a client-side "confirm password" match check.
- On success, the app stores `auth_token` (JWT) and `auth_user` (JSON) in `localStorage` and redirects to `/dashboard` (`AuthProvider.jsx`).
- All routes except `/login` are wrapped in `<ProtectedRoute>`, which redirects unauthenticated users back to `/login`.

## 2. Dashboard (`/dashboard`)

Shows six metric cards (Total Debt, Monthly Income, Monthly Expenses, Disposable Income, Debt-to-Income, Financial Health) plus a health-score ring and an active-loan list.

**As implemented today**, this page calls `GET /api/dashboard`, which is a hard-coded alias in `main.py` that **always returns zeros** and a static `"Submit your loan details..."` message — it does not query the database or reflect any loan a user has entered. If that call fails for any reason, the frontend instead shows hard-coded `PLACEHOLDER_DATA` (sample numbers like `$24,500` total debt). Either way, **the Dashboard is not currently driven by real user data.** See [Troubleshooting.md](Troubleshooting.md) for why, and [Future_Improvements.md](Future_Improvements.md) for the fix.

## 3. Settlement Predictor (`/settlement`) — Scenario 1

Form fields map to `POST /api/settlement/predict` (a `main.py` alias), which:

1. Accepts either the frontend's field names (`loan_amount`, `outstanding_balance`, `months_delinquent`, `monthly_payment_capacity`) or standard names, with fallback defaults for anything missing.
2. Runs `run_financial_analysis()` (the real scoring engine — see [System_Design.md](System_Design.md) §5).
3. Calls Gemini (or fallback) for a `negotiation_strategy` string.
4. Returns `recommended_settlement`, `settlement_percentage`, `monthly_payment_plan`, `confidence` (High/Medium/Low from health score), `strategy`, and `savings`.

This endpoint **is** functionally wired to the real financial engine (unlike the dashboard), it just doesn't persist the result to a specific user's loan record — see [API.md](API.md) for the exact contract.

## 4. Negotiation Email (`/negotiation`) — Scenario 2

Maps to `POST /api/negotiation/generate` (another `main.py` alias). Takes current balance, offer amount, income/expenses, lender/creditor name, and borrower name; runs the same financial engine, then calls Gemini/fallback with the lender and borrower names threaded through so the generated letter is personalized. Returns the letter under three different keys (`letter`, `content`, `negotiation_letter`) simultaneously, to tolerate whichever key name the frontend happens to read.

## 5. Know Your Rights (`/rights`) — Scenario 3 (partial)

Calls `GET /api/rights`, which returns a fixed, hard-coded list of six borrower-rights topics (FDCPA, debt validation, statute of limitations, credit reporting, settlement protections, right to negotiate). This content is entirely static in `main.py` — there is no rights database table or admin-editable content source.

## 6. History (`/history`)

Calls `GET /api/history`, which always returns an empty list with a `"Login to view your settlement and negotiation history"` message, **regardless of whether the user is logged in or has settlement records**. The database has the tables to support real history (`SettlementRecommendation`, `NegotiationLetter`), and `GET /api/v1/settlement/user/{user_id}` already exists and does query them — but the frontend's `/history` route calls the non-functional alias instead. See [Troubleshooting.md](Troubleshooting.md).

## 7. Using the "real" versioned API directly

Everything under `/api/v1/...` is the actual, fully wired implementation (routers in `Backend/app/api/`). A developer or API consumer who wants persisted, per-user data (loans, settlements tied to a `loan_id`, monthly financial history) should use the `/api/v1/...` endpoints documented in [API.md](API.md) rather than the `/api/...` aliases the current frontend happens to call.
