# Folder Structure

Annotated tree of the actual project (excludes `venv/`, `node_modules/`, `__pycache__/`, and `.git/`, which are build/dependency artifacts, not source).

```
AI Powered Debt Relief & Financial Recovery Platform/
│
├── Readme.md                       # Original project overview (3 scenarios)
├── .gitignore
│
├── Backend/                        # FastAPI application
│   ├── .gitignore
│   ├── requirements.txt            # Pinned Python dependencies
│   ├── debt_relief.db              # SQLite database file (created by init_database())
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app instance, CORS, routers, alias endpoints
│       ├── api/                    # HTTP route layer
│       │   ├── __init__.py
│       │   ├── health.py           # GET /api/v1/health/
│       │   ├── user.py             # /api/v1/auth/register, /login, /me (JWT auth)
│       │   ├── loan.py             # CRUD for loan records
│       │   ├── financial.py        # Financial analysis + monthly financial records
│       │   ├── settlement.py       # Settlement recommendation generation + retrieval
│       │   └── ai.py               # Negotiation letter generation + AI status
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py           # Settings (env vars, app metadata)
│       │   ├── database.py         # get_db() dependency, init_database()
│       │   └── security.py         # EMPTY FILE — see Troubleshooting.md
│       ├── services/                # Business logic layer
│       │   ├── __init__.py
│       │   ├── calculator.py       # EMI, ratio, settlement % math
│       │   ├── financial_engine.py # Orchestrates calculator + validators → analysis dict
│       │   ├── gemini_service.py   # Gemini AI call + prompt construction
│       │   └── fallback_service.py # Rule-based recommendation when AI unavailable
│       └── utils/
│           ├── __init__.py
│           ├── helpers.py          # round_to_two, safe_divide, overdue days, currency fmt
│           ├── validators.py       # Input validation raising ValidationError
│           └── exceptions.py       # Custom HTTPException subclasses
│
├── DataBase/                       # Shared data layer (imported via sys.path injection)
│   ├── database.py                 # SQLAlchemy engine/session/Base (separate from Backend's!)
│   ├── models.py                   # ORM models: User, Loan, MonthlyFinancial,
│   │                                #   SettlementRecommendation, NegotiationLetter, FinancialMetric
│   ├── schemas.py                  # Pydantic request schemas: UserCreate, LoanCreate,
│   │                                #   MonthlyFinancialCreate, SettlementCreate
│   ├── crud.py                     # Create/Read/Update/Delete functions used by Backend routers
│   ├── auth.py                     # Standalone auth module (bcrypt + JWT) — NOT used by Backend
│   ├── init_db.py                  # Script: run once to create tables
│   ├── db_optimization.py          # Script: adds indexes, runs ANALYZE
│   ├── settlement_prediction.py    # Alternative settlement-scoring engine (DB-driven)
│   └── loan_settlement_service.py  # Loan/settlement lifecycle business rules
│
├── Documents/
│   └── docs.txt                    # Free-form notes; not read by any application code
│
└── Frontend/vite-project/          # React SPA
    ├── index.html
    ├── package.json / package-lock.json
    ├── vite.config.js
    ├── eslint.config.js
    ├── .env.example                # VITE_API_BASE_URL
    ├── public/
    │   ├── favicon.svg
    │   └── icons.svg
    └── src/
        ├── main.jsx                 # ReactDOM root render
        ├── App.jsx                  # Router setup, route tree
        ├── App.css / index.css
        ├── assets/                  # hero.png, react.svg, vite.svg
        ├── components/
        │   ├── ProtectedRoute.jsx   # Redirects to /login if not authenticated
        │   ├── layout/
        │   │   ├── AppLayout.jsx    # Shell: Sidebar + <Outlet/>
        │   │   └── Sidebar.jsx      # Nav links
        │   └── ui/                  # Button, Card, Input, MetricCard (+ matching .css)
        ├── context/
        │   ├── authContext.js       # React Context object
        │   └── AuthProvider.jsx     # login/register/logout, localStorage persistence
        ├── hooks/
        │   └── useAuth.js           # useContext(AuthContext) wrapper
        ├── pages/
        │   ├── Login.jsx / .css
        │   ├── Dashboard.jsx / .css
        │   ├── SettlementPredictor.jsx / .css
        │   ├── NegotiationEmail.jsx / .css
        │   ├── KnowYourRights.jsx / .css
        │   └── History.jsx / .css
        └── services/
            └── api.js               # Central fetch() wrapper, all API calls
```

## Notable structural observations

- **Two `database.py` files with different responsibilities**: `Backend/app/core/database.py` (imports from `DataBase/database.py` and exposes `get_db`/`init_database` to the FastAPI app) and `DataBase/database.py` itself (defines the actual SQLAlchemy `engine`, `SessionLocal`, `Base`). This works only because of `sys.path.insert(...)` calls scattered across many files — see [Troubleshooting.md](Troubleshooting.md).
- **`Backend/debt_relief.db`** exists as a committed/generated file. `DataBase/database.py` also defines `SQLALCHEMY_DATABASE_URL = "sqlite:///./debt_relief.db"`, which is a **relative path** — the actual file created depends on the *current working directory* the process is launched from, not a fixed location. In practice this can silently produce two different `debt_relief.db` files in two different folders. **Inferred** from reading `DataBase/database.py` and the fact that a `debt_relief.db` file exists under `Backend/` (i.e., outside `DataBase/`).
- **`Backend/app/core/security.py` is empty** — its filename suggests it was intended to hold the JWT/password logic, but that logic instead lives directly in `app/api/user.py`.
