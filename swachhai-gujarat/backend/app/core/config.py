"""
Application configuration — reads from .env file.
Never expose secrets through this module.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    secret_key: str = "change-me"
    debug: bool = True
    demo_mode: bool = True

    # Database
    database_url: str = "sqlite:///./swachhai.db"

    # JWT
    jwt_secret: str = "change-me-jwt"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # AI Providers
    primary_llm_provider: str = "groq"
    fallback_llm_provider: str = "groq"

    # IBM watsonx.ai
    ibm_api_key: str = ""
    ibm_project_id: str = ""
    ibm_watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    ibm_granite_model: str = "ibm/granite-3-8b-instruct"

    # Groq
    groq_api_key: str = ""
    groq_primary_model: str = "llama-3.3-70b-versatile"
    groq_fast_model: str = "llama-3.1-8b-instant"

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
