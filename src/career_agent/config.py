"""The single place where configuration is read (env vars and `.env`).

Nothing here raises at import time. A missing GROQ_API_KEY only fails when an
LLM client is actually built (see `career_agent.clients.llm.get_llm_client`).
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root when running from a checkout / editable install (src/career_agent/config.py → ../..).
# Lets `streamlit run <abs path>` work from any cwd. A `.env` in the cwd takes precedence.
PROJECT_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT_ENV, ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # `GROQ_API_KEY=` (as in .env.example) counts as unset
        extra="ignore",
    )

    groq_api_key: SecretStr | None = None
    model_name: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.2
    # Reasoning models spend completion tokens on hidden reasoning before the answer,
    # so this budget must cover reasoning + the full report.
    llm_max_tokens: int = 8192
    # gpt-oss supports low|medium|high. Use "none" for non-reasoning models (param not sent).
    llm_reasoning_effort: Literal["none", "low", "medium", "high"] = "medium"

    github_api_url: str = "https://api.github.com"
    github_timeout_seconds: float = 10.0

    cv_max_chars: int = 3500

    log_level: str = "INFO"
    log_file: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
