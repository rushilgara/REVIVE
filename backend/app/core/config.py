import json
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "REVIVE"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Integration Mode: 'simulation' or 'real_test'
    INTEGRATION_MODE: str = "simulation"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./revive.db"

    # AI Provider: 'deterministic_fallback', 'openai', 'gemini'
    AI_PROVIDER: str = "deterministic_fallback"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Razorpay Test Mode Credentials (Backend Only - NEVER sent to frontend)
    RAZORPAY_KEY_ID: str = "rzp_test_revive_demo"
    RAZORPAY_KEY_SECRET: str = "revive_secret_key_12345"
    RAZORPAY_WEBHOOK_SECRET: str = "revive_webhook_secret_67890"

    # Security & CORS
    SECRET_KEY: str = "revive-super-secret-key-change-in-production"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Default Business / Policy Thresholds
    DEFAULT_APPROVAL_THRESHOLD_MINOR: int = 5000000  # ₹50,000 in paise
    MAX_RETRY_ATTEMPTS: int = 3
    MAX_CONTACT_ATTEMPTS: int = 4
    COOLDOWN_HOURS: int = 12

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            try:
                parsed = json.loads(self.CORS_ORIGINS)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            return [i.strip() for i in self.CORS_ORIGINS.split(",") if i.strip()]
        return ["*"]


settings = Settings()
