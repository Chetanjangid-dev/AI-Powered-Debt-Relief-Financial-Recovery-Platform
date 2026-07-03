# Glossary

| Term | Meaning in this project |
|---|---|
| **EMI** | Equated Monthly Installment — the fixed monthly payment amount on a loan, computed by `calculator.calculate_emi()` using the standard amortization formula. |
| **Outstanding balance** | The remaining unpaid principal (plus accrued interest, as entered by the user) on a loan, distinct from the original `loan_amount`. |
| **Debt stress level** | One of `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`, derived in `financial_engine.determine_debt_stress_level()` from EMI-to-income ratio and monthly surplus. |
| **Financial health score** | A 0–100 composite score summarizing a borrower's overall financial position. **Two different formulas exist** in this codebase (`financial_engine.py` vs. `settlement_prediction.py`) — see [Troubleshooting.md](Troubleshooting.md). |
| **Monthly surplus** | `monthly_income − monthly_expenses − EMI`. Negative means the borrower is in deficit even before accounting for other spending. |
| **EMI ratio** | `EMI / monthly_income × 100`. Industry rule of thumb: above 40% is considered high risk. |
| **DTI (Debt-to-Income) ratio** | `outstanding_balance / annual_income × 100` in `financial_engine.py`; a differently-scoped `total_monthly_debt_payments / monthly_income × 100` in `settlement_prediction.py` — these are **not the same calculation** despite the shared name. |
| **Settlement percentage** | The recommended fraction of the outstanding balance a lender might realistically accept as a one-time payoff, expressed as a percent (e.g., 65% of ₹80,000 = ₹52,000). |
| **Negotiation letter** | The AI- (or fallback-) generated formal settlement request letter text, addressed to the lender. |
| **Negotiation strategy** | A shorter, advisory paragraph (distinct from the letter) describing *how* to approach the negotiation, generated alongside the letter. |
| **Source (`gemini` \| `fallback`)** | Field returned by `call_gemini()` indicating whether the response came from the live Gemini API or the deterministic rule-based fallback engine. |
| **Alias endpoint** | An endpoint defined in `main.py` outside the `/api/v1` prefix, built to match the current frontend's exact expected path/field names — see [API.md](API.md). |
| **Versioned API** | The `/api/v1/...` endpoints, defined in `app/api/*.py` routers, registered via `settings.API_PREFIX`. |
| **Overdue days** | Number of days past `emi_due_date` (0 if no due date is provided or the loan isn't overdue). |
| **Settlement status** | Lifecycle state of a `SettlementRecommendation` row: `pending` → `accepted` or `rejected` (see `loan_settlement_service.py`). |
| **Loan status** | Lifecycle state of a `Loan` row: `active` → `settled` or `defaulted`. |
| **FDCPA** | Fair Debt Collection Practices Act — a U.S. federal law referenced in the static "Know Your Rights" content, protecting borrowers from abusive debt collection practices. |
