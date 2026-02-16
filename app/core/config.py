
from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext


# ==============================
# Security constants
# ==============================

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ==============================
# App Settings
# ==============================

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    COHERE_API_KEY: str   # 👈 هنا الصح

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Export globals
SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL
