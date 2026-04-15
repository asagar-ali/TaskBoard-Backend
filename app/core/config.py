import os
from dotenv import load_dotenv

load_dotenv()  # ✅ Actually call it, not assign it


class Config:
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_PUBLISHABLE_KEY: str = os.getenv("VITE_CLERK_PUBLISHABLE_KEY", "")
    CLERK_JWKS_URL: str = os.getenv("CLERK_JWKS_URL", "")
    CLERK_WEBHOOK_SECRET: str = os.getenv("CLERK_WEBHOOK_SECRET", "")  # ✅ Now read from .env

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    FREE_TIER_MEMBERSHIP_LIMIT: int = 2
    PRO_TIER_MEMBERSHIP_LIMIT: int = 0  # unlimited


settings = Config()