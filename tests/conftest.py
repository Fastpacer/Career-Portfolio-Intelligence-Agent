import pytest

from career_agent.clients.github import get_github_client
from career_agent.clients.llm import get_llm_client
from career_agent.config import Settings, get_settings
from career_agent.schemas import GitHubProfile, RepoSummary


class FakeLLM:
    def __init__(self, reply: str = "## Career Profile Scores\nok"):
        self.reply = reply
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.reply


class FakeGitHub:
    def __init__(self, profile: GitHubProfile | None = None):
        self.profile = profile or GitHubProfile(
            repos=[RepoSummary(name="proj", description="A project", stars=3, language="Python")],
            repo_count=1,
            total_stars=3,
            top_languages={"Python": 1},
        )
        self.usernames: list[str] = []

    def fetch_profile(self, username: str) -> GitHubProfile:
        self.usernames.append(username)
        return self.profile


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch, tmp_path):
    """Never read the developer's real .env or keys; reset cached singletons."""
    monkeypatch.chdir(tmp_path)
    # Only the (empty) tmp cwd .env, never the developer's repo-root .env.
    monkeypatch.setitem(Settings.model_config, "env_file", ".env")
    for var in (
        "GROQ_API_KEY",
        "MODEL_NAME",
        "LLM_MAX_TOKENS",
        "LLM_REASONING_EFFORT",
        "GITHUB_API_URL",
        "CV_MAX_CHARS",
    ):
        monkeypatch.delenv(var, raising=False)
    for cached in (get_settings, get_llm_client, get_github_client):
        cached.cache_clear()
    yield
    for cached in (get_settings, get_llm_client, get_github_client):
        cached.cache_clear()


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def fake_github():
    return FakeGitHub()


def make_pdf(text: str) -> bytes:
    """Build a minimal single-page PDF containing `text` (no extra deps)."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return bytes(out)
