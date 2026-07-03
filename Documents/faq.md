# FAQ

**Q: Do I need a Gemini API key to run this project?**
No. If `GEMINI_API_KEY` is unset (or shorter than 10 characters), the app automatically uses `fallback_service.py`'s rule-based recommendation engine, which returns the same JSON shape as a real Gemini response. The app is fully functional without any AI key, just less personalized.

**Q: Why do the Dashboard and History pages show data that doesn't match what I entered?**
Those two pages currently call hard-coded alias endpoints (`/api/dashboard`, `/api/history`) that always return static placeholder data, not real database queries. See [Troubleshooting.md](Troubleshooting.md).

**Q: Why does the settlement percentage I get from `/financial/predict-settlement/{user_id}` differ from what `/settlement/recommend` gives me for what feels like the same situation?**
They use two different, independently implemented scoring formulas. See [Troubleshooting.md](Troubleshooting.md) for a side-by-side comparison.

**Q: Is this project production-ready?**
No — see [Security.md](Security.md) for critical issues (hard-coded JWT secret, missing resource-ownership checks, permissive CORS) that must be fixed first.

**Q: What database does this use, and can I switch to Postgres/MySQL?**
SQLite via SQLAlchemy. Since the ORM layer (`models.py`) uses standard SQLAlchemy constructs, switching the `SQLALCHEMY_DATABASE_URL` in `DataBase/database.py` to a Postgres/MySQL connection string plus installing the appropriate driver (`psycopg2`, `pymysql`) should work with minimal model changes, though this hasn't been tested in the current codebase.

**Q: Where do I add support for a new loan type or a new field on the loan form?**
Add the column to `Loan` in `DataBase/models.py`, add the field to `LoanCreate` in `DataBase/schemas.py`, and update the corresponding React form in `SettlementPredictor.jsx` / wherever loans are created. Remember there's no migration tool, so existing SQLite databases won't automatically get the new column — you'd need to delete/recreate the `.db` file in development, or write a manual `ALTER TABLE`.

**Q: What's the difference between `/api/...` and `/api/v1/...` endpoints?**
`/api/v1/...` are the "real," fully-wired routers under `Backend/app/api/`. `/api/...` (no version) are compatibility aliases defined directly in `main.py` to match the current React frontend's exact expected paths/field names. See [API.md](API.md) for the full breakdown of which is which and what each actually does.

**Q: Can multiple users use the app at the same time with SQLite?**
SQLite supports concurrent reads but serializes writes; for the traffic level of a demo/small deployment this works via `check_same_thread=False`, but it is not recommended for meaningful concurrent write load. See [Deployment.md](Deployment.md) for the recommendation to migrate to a networked database for production.

**Q: How is EMI calculated?**
Standard amortization formula in `calculator.py`: `EMI = P × r × (1+r)^n / ((1+r)^n − 1)`, where `r` is the monthly interest rate and `n` is tenure in months. If `annual_rate == 0`, it falls back to a simple `principal / tenure_months` split.

**Q: Where does the "financial health score" come from?**
Two different formulas exist depending on which endpoint you call — see [AI_Model.md](AI_Model.md) and [Troubleshooting.md](Troubleshooting.md).
