import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    # Application
    APP_NAME: str = "AI Powered Debt Relief & Financial Recovery Platform"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Database
    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./debt_relief.db"
   )

    # Google Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # OpenRouter AI (fallback when Gemini quota exhausted)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"


settings = Settings()