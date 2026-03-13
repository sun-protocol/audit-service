import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Audit Service"
    DATABASE_URL: str = "sqlite:///./audit_service.db"
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret-key"
    WORKSPACES_DIR: str = str(Path(__file__).resolve().parent.parent / "workspaces")
    SKILLS_CACHE_DIR: str = str(Path(__file__).resolve().parent.parent / "workspaces" / "_skills_cache")
    OPENCODE_BIN: str = "opencode"
    GIT_SSL_NO_VERIFY: bool = False
    DEFAULT_SCAN_PROMPT: str = (
        "Perform a comprehensive security review of this codebase. "
        "Identify vulnerabilities, insecure coding patterns, hardcoded secrets, "
        "dependency risks, and provide a summary with severity ratings."
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

os.makedirs(settings.WORKSPACES_DIR, exist_ok=True)
os.makedirs(settings.SKILLS_CACHE_DIR, exist_ok=True)
