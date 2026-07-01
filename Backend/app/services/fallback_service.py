from typing import Optional


def generate_fallback_recommendation(
    debt_stress_level: str,
    financial_health_score: float,
    emi_ratio: float,
    monthly_surplus: float,
    outstanding_balance: float,
    recommended_settlement_amount: float,
    settlement_percentage: float,
) -> dict:
    """
    Generates a rule-based settlement recommendation when Gemini AI is unavailable.
    This ensures the platform always returns useful output even without AI.
    Returns a structured recommendation matching the format Gemini would return.
    """

    strategy = _get_strategy(debt_stress_level, emi_ratio, monthly_surplus)
    letter = _generate_letter(
        debt_stress_level,
        monthly_surplus,
        outstanding_balance,
        recommended_settlement_amount,
        settlement_percentage,
    )
    tips = _get_financial_tips(debt_stress_level, emi_ratio, monthly_surplus)

    return {
        "source": "fallback",
        "recommendation_summary": strategy["summary"],
        "negotiation_strategy": strategy["strategy"],
        "suggested_offer": recommended_settlement_amount,
        "offer_percentage": settlement_percentage,
        "negotiation_letter": letter,
        "financial_tips": tips,
        "health_score": financial_health_score,
        "stress_level": debt_stress_level,
    }


def _get_strategy(
    stress_level: str,
    emi_ratio: float,
    monthly_surplus: float
) -> dict:
    """Returns negotiation summary and strategy based on stress level."""

    if stress_level == "CRITICAL":
        return {
            "summary": "Your financial situation requires immediate attention. "
                       "A significant settlement reduction is recommended.",
            "strategy": (
                "Given your critical debt stress level and high EMI burden, "
                "we recommend approaching your lender immediately with a one-time "
                "settlement offer. Highlight your inability to continue regular EMIs "
                "and request a 40-50% reduction on the outstanding balance. "
                "Consider seeking legal or financial counseling before negotiation."
            ),
        }
    elif stress_level == "HIGH":
        return {
            "summary": "Your EMI burden is high. A structured settlement negotiation "
                       "is advised to prevent further default.",
            "strategy": (
                "Your EMI-to-income ratio indicates financial strain. "
                "Request a settlement meeting with your lender and propose "
                "a lump-sum payment of 50-60% of the outstanding amount. "
                "Emphasize your willingness to resolve the debt and provide "
                "bank statements showing limited repayment capacity."
            ),
        }
    elif stress_level == "MEDIUM":
        return {
            "summary": "You are managing your debt but approaching a stress zone. "
                       "Proactive negotiation can prevent future difficulties.",
            "strategy": (
                "Your financial position allows for moderate negotiation. "
                "Approach your lender with a restructuring request — either "
                "a tenure extension to reduce EMI pressure, or a settlement "
                "offer of 60-70% of outstanding balance. Maintain regular "
                "communication with your lender to show good faith."
            ),
        }
    else:  # LOW
        return {
            "summary": "Your financial health is stable. "
                       "You are in a strong position to negotiate favorable terms.",
            "strategy": (
                "With a healthy surplus and manageable EMI ratio, you can "
                "negotiate from a position of strength. Consider requesting "
                "an interest rate reduction or prepayment discount from your lender. "
                "A settlement offer of 70-85% of outstanding balance is realistic "
                "given your strong repayment history."
            ),
        }


def _generate_letter(
    stress_level: str,
    monthly_surplus: float,
    outstanding_balance: float,
    settlement_amount: float,
    settlement_percentage: float,
) -> str:
    """Generates a professional settlement request letter."""

    return f"""Subject: Request for One-Time Settlement – Loan Account

Dear Sir/Madam,

I am writing to formally request consideration for a one-time settlement 
of my outstanding loan balance.

My current outstanding balance stands at ₹{outstanding_balance:,.2f}. 
After a thorough review of my financial situation, I have determined that 
my monthly surplus is ₹{monthly_surplus:,.2f}, which limits my ability 
to continue regular EMI payments as originally agreed.

Given my current financial constraints (Debt Stress Level: {stress_level}), 
I would like to propose a one-time settlement of ₹{settlement_amount:,.2f}, 
which represents {settlement_percentage}% of the outstanding balance.

I believe this settlement is fair and reflects my genuine repayment capacity. 
I am committed to making this payment promptly upon your approval.

I kindly request you to review my proposal and provide your response at 
the earliest convenience. I am open to discussion and can provide supporting 
financial documents upon request.

Thank you for your understanding and cooperation.

Yours sincerely,
[Borrower Name]
[Contact Information]
[Date]"""


def _get_financial_tips(
    stress_level: str,
    emi_ratio: float,
    monthly_surplus: float
) -> list:
    """Returns actionable financial improvement tips based on borrower's situation."""

    tips = []

    if emi_ratio > 40:
        tips.append(
            "Your EMI exceeds 40% of income. Consider requesting a loan tenure "
            "extension to reduce your monthly EMI burden."
        )

    if monthly_surplus < 5000:
        tips.append(
            "Your monthly surplus is very low. Review discretionary expenses "
            "and identify areas where spending can be reduced."
        )

    if stress_level in ["HIGH", "CRITICAL"]:
        tips.append(
            "Prioritize clearing high-interest debt first. "
            "Avoid taking new loans until existing obligations are resolved."
        )
        tips.append(
            "Consider consulting a certified financial advisor or "
            "debt counseling service for personalized guidance."
        )

    if stress_level == "LOW":
        tips.append(
            "Maintain an emergency fund of at least 3-6 months of expenses "
            "to protect against future financial shocks."
        )
        tips.append(
            "Your strong financial position makes you eligible for better "
            "loan terms. Consider refinancing at a lower interest rate."
        )

    if not tips:
        tips.append(
            "Continue maintaining your current financial discipline. "
            "Regular EMI payments improve your credit score over time."
        )

    return tips