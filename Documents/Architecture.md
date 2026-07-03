# Architecture

## 1. Style

The system is a classic **3-tier web application**:

- **Presentation tier** — React SPA (Vite build), talks to the backend exclusively over HTTP/JSON.
- **Application tier** — FastAPI backend, split into routers → services → utils, plus a "Database" package that is treated as a semi-external shared library.
- **Data tier** — SQLite file (`debt_relief.db`), accessed through SQLAlchemy ORM models.

There is no message queue, no caching layer, and no microservices — it is a single deployable backend process and a single static-asset frontend build.

## 2. High-Level Architecture Diagram

```mermaid
flowchart LR
    subgraph Client["Browser"]
        SPA["React SPA (Vite)\nReact Router, AuthProvider"]
    end

    subgraph Backend["FastAPI Backend (Uvicorn)"]
        MAIN["main.py\n(app instance + alias endpoints)"]
        ROUTERS["Routers\nhealth / user / loan / financial / settlement / ai"]
        SERVICES["Services\nfinancial_engine, calculator,\ngemini_service, fallback_service"]
        CORE["core\nconfig.py, database.py"]
    end

    subgraph DataLayer["DataBase package (shared)"]
        MODELS["models.py (SQLAlchemy ORM)"]
        SCHEMAS["schemas.py (Pydantic)"]
        CRUD["crud.py"]
        EXTRA["settlement_prediction.py\nloan_settlement_service.py\nauth.py (unused)"]
    end

    DB[("SQLite\ndebt_relief.db")]
    GEMINI[["Google Gemini API"]]

    SPA -- "fetch() JSON over HTTP" --> MAIN
    MAIN --> ROUTERS
    ROUTERS --> SERVICES
    ROUTERS --> CRUD
    SERVICES --> GEMINI
    SERVICES -. "fallback if\nGemini fails" .-> SERVICES
    CRUD --> MODELS
    MODELS --> DB
    CORE --> DB
```

## 3. Why this structure

- **Router → Service → Utils layering (backend)**: each FastAPI router module (`app/api/*.py`) is a thin HTTP adapter. Business logic (EMI math, health scoring, AI prompt construction) lives in `app/services/*.py`, and small stateless helpers live in `app/utils/*.py`. This is a reasonable, standard FastAPI layering choice.
- **Shared `DataBase/` package**: models, Pydantic schemas, and CRUD functions live in a top-level `DataBase/` folder rather than inside `Backend/app/`, and the backend adds that folder to `sys.path` at runtime (see `Backend/app/core/database.py` and nearly every router file). **Inferred**: this reflects a team split where one member ("Khushi", per code comments) owned the database layer independently of the FastAPI backend, and the two were integrated via `sys.path` manipulation rather than a proper installable package or shared library. This works but is fragile — see [Future_Improvements.md](Future_Improvements.md).
- **AI service with fallback**: `gemini_service.call_gemini()` always returns a valid recommendation dict, either from Gemini or from `fallback_service.generate_fallback_recommendation()`. This guarantees the two AI-dependent endpoints (`/settlement/recommend`, `/ai/negotiation-letter`) never hard-fail due to AI unavailability — a deliberate resilience pattern.
- **Compatibility alias layer in `main.py`**: a large block of duplicate endpoints exists purely to match a specific frontend implementation's expected URL paths and JSON field names (see [Troubleshooting.md](Troubleshooting.md)). This is not a designed architectural layer — it is an integration patch.

## 4. Component Diagram

```mermaid
flowchart TB
    subgraph Frontend
        Pages["Pages: Login, Dashboard,\nSettlementPredictor, NegotiationEmail,\nKnowYourRights, History"]
        UIComp["UI components: Button, Card, Input, MetricCard"]
        Layout["AppLayout / Sidebar / ProtectedRoute"]
        AuthCtx["AuthProvider / useAuth (Context API)"]
        ApiClient["services/api.js (fetch wrapper)"]
    end

    subgraph BackendApp["Backend/app"]
        direction TB
        HealthR["api/health.py"]
        UserR["api/user.py (auth: register/login/me)"]
        LoanR["api/loan.py"]
        FinR["api/financial.py"]
        SettR["api/settlement.py"]
        AiR["api/ai.py"]
        FinEngine["services/financial_engine.py"]
        Calc["services/calculator.py"]
        Gemini["services/gemini_service.py"]
        Fallback["services/fallback_service.py"]
        Helpers["utils/helpers.py, validators.py, exceptions.py"]
        Config["core/config.py"]
        DbCore["core/database.py"]
    end

    subgraph DataBase
        Models["models.py"]
        Schemas["schemas.py"]
        Crud["crud.py"]
        SettlePred["settlement_prediction.py"]
        LoanSvc["loan_settlement_service.py"]
        DbEngine["database.py (engine/session/Base)"]
    end

    Pages --> ApiClient
    AuthCtx --> ApiClient
    Layout --> Pages
    ApiClient -->|HTTP| HealthR & UserR & LoanR & FinR & SettR & AiR

    UserR --> Models
    LoanR --> Crud
    FinR --> FinEngine
    FinR --> SettlePred
    SettR --> FinEngine
    SettR --> Gemini
    AiR --> FinEngine
    AiR --> Gemini
    FinEngine --> Calc
    FinEngine --> Helpers
    Gemini --> Fallback
    Crud --> Models
    Models --> DbEngine
    DbCore --> DbEngine
```

## 5. Deployment Diagram

```mermaid
flowchart LR
    subgraph DevMachine["Developer machine / single VM"]
        subgraph FE["Frontend process"]
            Vite["vite dev server :5173\n(or static build served by\nnginx / any static host)"]
        end
        subgraph BE["Backend process"]
            Uvicorn["uvicorn app.main:app :8000"]
        end
        SQLite[("debt_relief.db\n(local file)")]
    end
    Browser["User's Browser"]
    Gemini[["Google Gemini API\n(generativelanguage.googleapis.com)"]]

    Browser <--> Vite
    Browser <--> Uvicorn
    Uvicorn <--> SQLite
    Uvicorn <--> Gemini
```

There is no containerization, orchestration, or IaC in the repository — deployment today is manual process-per-machine. See [Deployment.md](Deployment.md) for recommended productionization steps.
