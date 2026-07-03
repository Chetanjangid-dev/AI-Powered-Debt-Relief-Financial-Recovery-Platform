# System Design

## 1. Request Lifecycle Diagram

Generic lifecycle for any versioned API call (`/api/v1/...`):

```mermaid
flowchart LR
    A["Browser: fetch() via api.js"] --> B["Uvicorn ASGI server"]
    B --> C["FastAPI CORSMiddleware"]
    C --> D["Router match\n(app/api/*.py)"]
    D --> E["Pydantic request validation"]
    E -->|invalid| F["422 Unprocessable Entity"]
    E -->|valid| G["Depends(get_db) opens\nSQLAlchemy session"]
    G --> H["Route handler:\nservice calls / crud calls"]
    H --> I["Response serialized to JSON"]
    I --> J["Session closed (finally block)"]
    J --> K["Browser receives JSON"]
```

## 2. Sequence Diagram — Scenario 1: AI-Powered Settlement Recommendation

This is the "real" versioned flow (`POST /api/v1/settlement/recommend`), as opposed to the simplified alias (`POST /api/settlement/predict`) described in [Troubleshooting.md](Troubleshooting.md).

```mermaid
sequenceDiagram
    participant U as Borrower (Browser)
    participant API as FastAPI /settlement/recommend
    participant FE as financial_engine
    participant GS as gemini_service
    participant G as Google Gemini API
    participant FB as fallback_service
    participant DB as SQLite (via crud)

    U->>API: POST loan + income data
    API->>FE: run_financial_analysis(...)
    FE->>FE: validate inputs
    FE->>FE: calculate_emi, surplus, ratios
    FE->>FE: determine_debt_stress_level
    FE->>FE: calculate_financial_health_score
    FE->>FE: calculate_settlement_percentage
    FE-->>API: analysis dict
    API->>GS: call_gemini(analysis fields)
    alt GEMINI_API_KEY missing or API call fails
        GS->>FB: generate_fallback_recommendation(...)
        FB-->>GS: rule-based recommendation
    else Gemini succeeds
        GS->>G: generate_content(prompt)
        G-->>GS: JSON text (summary, strategy, letter, tips)
        GS->>GS: parse JSON
    end
    GS-->>API: recommendation dict (source: gemini|fallback)
    API->>DB: crud.create_settlement(...)
    DB-->>API: saved SettlementRecommendation row
    API-->>U: { recommendation, analysis }
```

## 3. Sequence Diagram — Scenario 2: Intelligent Negotiation Letter Generation

```mermaid
sequenceDiagram
    participant U as Borrower
    participant API as FastAPI /ai/negotiation-letter
    participant FE as financial_engine
    participant GS as gemini_service

    U->>API: POST loan + income + lender/borrower names
    API->>FE: run_financial_analysis(...)
    FE-->>API: analysis dict
    API->>GS: call_gemini(..., lender_name, borrower_name)
    GS-->>API: negotiation_letter, strategy, tips, source
    API-->>U: full negotiation response
```

## 4. Sequence Diagram — Authentication (register / login)

```mermaid
sequenceDiagram
    participant U as Browser
    participant API as FastAPI /api/v1/auth/*
    participant DB as SQLite (User table)

    U->>API: POST /register {name, email, password}
    API->>DB: check existing email
    alt email exists
        API-->>U: 400 Email already registered
    else new user
        API->>API: hash_password (sha256_crypt)
        API->>DB: INSERT User
        API->>API: create_token (JWT, HS256, 60 min expiry)
        API-->>U: { token, user }
    end

    U->>API: POST /login {email, password}
    API->>DB: SELECT user by email
    API->>API: verify_password
    alt invalid
        API-->>U: 401 Invalid email or password
    else valid
        API->>API: create_token
        API-->>U: { token, user }
    end

    U->>API: GET /me (Authorization: Bearer <token>)
    API->>API: decode_token
    API->>DB: SELECT user by email from token
    API-->>U: { user }
```

## 5. Data Flow Diagram (Financial Analysis Engine)

```mermaid
flowchart TD
    In["Inputs: loan_amount, outstanding_balance,\ninterest_rate, tenure_months,\nmonthly_income, monthly_expenses,\n(optional) emi_amount, emi_due_date"]
    Val["Validators:\nvalidate_positive, validate_percentage,\nvalidate_income_vs_expenses,\nvalidate_loan_amount_vs_balance"]
    EMI["calculate_emi()\n(standard amortization formula)"]
    Overdue["calculate_overdue_days()"]
    Surplus["calculate_monthly_surplus()"]
    EmiRatio["calculate_emi_ratio()"]
    DTI["calculate_debt_to_income_ratio()"]
    ExpRatio["calculate_expense_ratio()"]
    Stress["determine_debt_stress_level()"]
    Health["calculate_financial_health_score()"]
    SettlePct["calculate_settlement_percentage()"]
    SettleAmt["settlement_amount =\noutstanding_balance * settlement_pct / 100"]
    Out["Output: analysis dict\n(emi_amount, monthly_surplus, emi_ratio,\ndebt_to_income_ratio, expense_ratio,\noverdue_days, debt_stress_level,\nfinancial_health_score, settlement_percentage,\nrecommended_settlement_amount)"]

    In --> Val --> EMI
    EMI --> Surplus
    Overdue --> Health
    Surplus --> EmiRatio --> Stress
    Surplus --> Stress
    EMI --> EmiRatio
    In --> DTI
    In --> ExpRatio --> Health
    EmiRatio --> Health
    Surplus --> Health
    Stress --> Out
    Health --> SettlePct --> SettleAmt --> Out
    DTI --> Out
```

## 6. State Diagram — Loan Lifecycle

Defined by `DataBase/loan_settlement_service.py` (business logic that is written but only partially wired to the API — see [Troubleshooting.md](Troubleshooting.md)).

```mermaid
stateDiagram-v2
    [*] --> active: Loan created
    active --> settled: outstanding_balance reaches 0\n(via record_payment or accept_settlement)
    active --> defaulted: mark_loan_defaulted()
    settled --> [*]
    defaulted --> [*]
```

## 7. State Diagram — Settlement Recommendation Lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending: create_settlement_offer()
    pending --> accepted: accept_settlement()\n(loan balance zeroed, loan → settled)
    pending --> rejected: reject_settlement()
    accepted --> [*]
    rejected --> [*]
```

## 8. Activity Diagram — Gemini Call with Fallback

```mermaid
flowchart TD
    Start(["call_gemini() invoked"]) --> CheckKey{"GEMINI_API_KEY set\nand length >= 10?"}
    CheckKey -- No --> Fallback["generate_fallback_recommendation()"]
    CheckKey -- Yes --> BuildPrompt["_build_prompt(...)"]
    BuildPrompt --> CallAPI["genai.Client.models.generate_content()"]
    CallAPI --> TryParse{"Response text\nparses as JSON?"}
    TryParse -- "Exception at any step" --> Fallback
    TryParse -- Yes --> ReturnGemini["Return dict with source='gemini'"]
    Fallback --> ReturnFallback["Return dict with source='fallback'\n(+ gemini_error if applicable)"]
    ReturnGemini --> End(["Caller receives\nrecommendation dict"])
    ReturnFallback --> End
```
