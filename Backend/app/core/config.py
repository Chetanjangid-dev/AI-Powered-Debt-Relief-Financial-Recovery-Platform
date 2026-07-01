import os
from dotenv import load_dotenv

# Load .env file from Backend/ directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


class Settings:
    # Application
    APP_NAME: str = "AI Powered Debt Relief & Financial Recovery Platform"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///../Database/debt_relief.db"  # fallback if .env missing
    )

    # Google Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"


# Single instance used across the entire backend
settings = Settings()