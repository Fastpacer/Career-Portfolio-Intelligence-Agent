import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from career_agent.clients.llm import GroqLLMClient, LLMConfigError, get_llm_client
from career_agent.config import Settings


def test_importing_modules_without_key_does_not_raise(tmp_path):
    # Regression for I-5: the old groq_service raised RuntimeError at import time.
    env = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
    result = subprocess.run(
        [sys.executable, "-c", "import career_agent, career_agent.clients.llm, api.main"],
        cwd=tmp_path,
        env={**env, "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not list(tmp_path.glob("*.log")), "importing must not create log files"


def test_missing_key_raises_only_when_client_is_built():
    with pytest.raises(LLMConfigError, match="GROQ_API_KEY"):
        get_llm_client()


def test_empty_key_in_dotenv_counts_as_missing(tmp_path):
    (tmp_path / ".env").write_text("GROQ_API_KEY=\n")

    with pytest.raises(LLMConfigError):
        get_llm_client()


def test_settings_read_from_dotenv_in_cwd(tmp_path):
    (tmp_path / ".env").write_text("GROQ_API_KEY=from-dotenv\nMODEL_NAME=some/model\n")

    s = Settings()

    assert s.groq_api_key.get_secret_value() == "from-dotenv"
    assert s.model_name == "some/model"


def test_settings_find_project_root_dotenv_from_any_cwd(tmp_path, monkeypatch):
    # Regression: `streamlit run <abs path>` launched from a parent directory found no .env.
    root_env = tmp_path / "repo" / ".env"
    root_env.parent.mkdir()
    root_env.write_text("GROQ_API_KEY=from-root\n")
    monkeypatch.setitem(Settings.model_config, "env_file", (root_env, ".env"))

    assert Settings().groq_api_key.get_secret_value() == "from-root"

    (tmp_path / ".env").write_text("GROQ_API_KEY=from-cwd\n")
    assert Settings().groq_api_key.get_secret_value() == "from-cwd"


def test_api_key_is_not_leaked_in_repr(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "super-secret")

    assert "super-secret" not in repr(Settings())


class _RecordingCompletions:
    def __init__(self, content="report", finish_reason="stop"):
        self.kwargs = None
        self._response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content), finish_reason=finish_reason
                )
            ],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20),
        )

    def create(self, **kwargs):
        self.kwargs = kwargs
        return self._response


def _client_with_fake_transport(completions):
    client = GroqLLMClient(Settings())
    client._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return client


def test_groq_client_defaults_to_gpt_oss_with_reasoning(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "k")
    completions = _RecordingCompletions()

    assert _client_with_fake_transport(completions).complete("hi") == "report"
    kw = completions.kwargs
    assert kw["model"] == "openai/gpt-oss-120b"
    assert kw["reasoning_effort"] == "medium"
    assert kw["include_reasoning"] is False
    assert kw["max_completion_tokens"] == 8192
    assert "max_tokens" not in kw


def test_reasoning_params_omitted_for_non_reasoning_models(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "k")
    monkeypatch.setenv("MODEL_NAME", "llama-3.3-70b-versatile")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "none")
    completions = _RecordingCompletions()

    _client_with_fake_transport(completions).complete("hi")

    assert completions.kwargs["model"] == "llama-3.3-70b-versatile"
    assert "reasoning_effort" not in completions.kwargs
    assert "include_reasoning" not in completions.kwargs


def test_truncated_output_is_still_returned(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "k")
    completions = _RecordingCompletions(content="partial", finish_reason="length")

    assert _client_with_fake_transport(completions).complete("hi") == "partial"
