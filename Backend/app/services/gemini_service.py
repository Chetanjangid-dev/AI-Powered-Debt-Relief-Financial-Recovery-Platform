import os
import sys
import json
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "Database"))

from app.core.config import settings
from app.services.fallback_service import generate_fallback_recommendation


def _build_prompt(
    debt_stress_level: str,
    financial_health_score: float,
    emi_ratio: float,
    monthly_surplus: float,
    outstanding_balance: float,
    recommended_settlement_amount: float,
    settlement_percentage: float,
    lender_name: str = "the Lender",
    borrower_name: str = "[Borrower Name]",
) -> str:
    """
    Builds a detailed prompt for Gemini AI based on borrower's financial profile.
    The more specific the prompt, the better the AI response.
    """
    return f"""
You are a professional financial advisor specializing in debt settlement and negotiation.

A borrower needs your help with debt settlement. Here is their complete financial profile:

FINANCIAL METRICS:
- Debt Stress Level: {debt_stress_level}
- Financial Health Score: {financial_health_score}/100
- EMI-to-Income Ratio: {emi_ratio}%
- Monthly Surplus: Rs.{monthly_surplus:,.2f}
- Outstanding Balance: Rs.{outstanding_balance:,.2f}
- Recommended Settlement Amount: Rs.{recommended_settlement_amount:,.2f}
- Settlement Offer Percentage: {settlement_percentage}%
- Lender Name: {lender_name}
- Borrower Name: {borrower_name}

Based on this financial profile, provide:

1. RECOMMENDATION_SUMMARY: A 2-3 sentence summary of the borrower's situation and recommended action.

2. NEGOTIATION_STRATEGY: A detailed 4-6 sentence strategy for negotiating with the lender, specific to this borrower's stress level and financial capacity.

3. NEGOTIATION_LETTER: A complete, professional settlement request letter addressed to {lender_name} from {borrower_name}. Include specific amounts and percentages. Make it formal and persuasive.

4. FINANCIAL_TIPS: Exactly 3 specific, actionable tips for improving this borrower's financial situation.

Respond ONLY in this exact JSON format with no extra text:
{{
    "recommendation_summary": "...",
    "negotiation_strategy": "...",
    "negotiation_letter": "...",
    "financial_tips": ["tip1", "tip2", "tip3"]
}}
"""


def call_gemini(
    debt_stress_level: str,
    financial_health_score: float,
    emi_ratio: float,
    monthly_surplus: float,
    outstanding_balance: float,
    recommended_settlement_amount: float,
    settlement_percentage: float,
    lender_name: str = "the Lender",
    borrower_name: str = "[Borrower Name]",
) -> dict:
    """
    Calls Google Gemini API to generate AI-powered settlement recommendation.
    Falls back to rule-based system if:
    - API key is missing
    - Gemini API call fails
    - Response cannot be parsed
    This ensures the platform ALWAYS returns a useful response.

    Returns: dict with source ('gemini' or 'fallback') + recommendation fields
    """

    # Check API key exists and has valid length
    if not settings.GEMINI_API_KEY or len(settings.GEMINI_API_KEY) < 10:
        print("WARNING: GEMINI_API_KEY not set. Using fallback service.")
        return generate_fallback_recommendation(
            debt_stress_level=debt_stress_level,
            financial_health_score=financial_health_score,
            emi_ratio=emi_ratio,
            monthly_surplus=monthly_surplus,
            outstanding_balance=outstanding_balance,
            recommended_settlement_amount=recommended_settlement_amount,
            settlement_percentage=settlement_percentage,
        )

    try:
        from google import genai

        # Initialize Gemini client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Build the prompt
        prompt = _build_prompt(
            debt_stress_level=debt_stress_level,
            financial_health_score=financial_health_score,
            emi_ratio=emi_ratio,
            monthly_surplus=monthly_surplus,
            outstanding_balance=outstanding_balance,
            recommended_settlement_amount=recommended_settlement_amount,
            settlement_percentage=settlement_percentage,
            lender_name=lender_name,
            borrower_name=borrower_name,
        )

        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )

        # Extract text response
        raw_text = response.text.strip()

        # Clean markdown code fences if Gemini wraps response in them
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        # Parse JSON response from Gemini
        parsed = json.loads(raw_text)

        return {
            "source": "gemini",
            "recommendation_summary": parsed.get("recommendation_summary", ""),
            "negotiation_strategy": parsed.get("negotiation_strategy", ""),
            "negotiation_letter": parsed.get("negotiation_letter", ""),
            "financial_tips": parsed.get("financial_tips", []),
            "suggested_offer": recommended_settlement_amount,
            "offer_percentage": settlement_percentage,
            "health_score": financial_health_score,
            "stress_level": debt_stress_level,
        }

    except Exception as e:
        # Any failure → gracefully fall back to rule-based system
        # Backend never crashes — always returns useful response
        print(f"WARNING: Gemini API error: {str(e)}. Switching to fallback service.")
        result = generate_fallback_recommendation(
            debt_stress_level=debt_stress_level,
            financial_health_score=financial_health_score,
            emi_ratio=emi_ratio,
            monthly_surplus=monthly_surplus,
            outstanding_balance=outstanding_balance,
            recommended_settlement_amount=recommended_settlement_amount,
            settlement_percentage=settlement_percentage,
        )
        result["gemini_error"] = str(e)
        return result