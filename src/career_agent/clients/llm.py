from functools import lru_cache
from typing import Protocol

from career_agent.config import Settings, get_settings
from career_agent.logging import logger


class LLMConfigError(RuntimeError):
    """Raised when the LLM client cannot be built (e.g. missing API key)."""


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class GroqLLMClient:
    def __init__(self, settings: Settings):
        if settings.groq_api_key is None:
            raise LLMConfigError(
                "GROQ_API_KEY is not set. Add it to .env, the environment, "
                "or .streamlit/secrets.toml."
            )
        from groq import Groq

        self._client = Groq(api_key=settings.groq_api_key.get_secret_value())
        self._settings = settings

    def complete(self, prompt: str) -> str:
        s = self._settings
        extra = {}
        if s.llm_reasoning_effort != "none":
            # Keep the model's chain of thought out of the returned content.
            extra = {"reasoning_effort": s.llm_reasoning_effort, "include_reasoning": False}
        response = self._client.chat.completions.create(
            model=s.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=s.llm_temperature,
            max_completion_tokens=s.llm_max_tokens,
            top_p=0.9,
            **extra,
        )
        choice = response.choices[0]
        usage = response.usage
        logger.info(
            "LLM call model={} finish_reason={} prompt_tokens={} completion_tokens={}",
            s.model_name,
            choice.finish_reason,
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
        )
        if choice.finish_reason == "length":
            logger.warning(
                "LLM output truncated at {} tokens; raise LLM_MAX_TOKENS", s.llm_max_tokens
            )
        return choice.message.content or ""


@lru_cache
def get_llm_client() -> LLMClient:
    return GroqLLMClient(get_settings())
