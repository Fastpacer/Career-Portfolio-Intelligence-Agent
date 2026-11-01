# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This is a career analysis tool. The user uploads a CV (PDF) and enters a GitHub username and a target role. The app returns an LLM-generated Markdown report with these parts:
- scores: ATS, portfolio, skill alignment, and overall
- skill gaps
- portfolio and resume improvements
- a 30-day roadmap

The LLM is Groq; the default model is `openai/gpt-oss-120b`. This is a **reasoning model**: hidden reasoning tokens count against `LLM_MAX_TOKENS`, which is sent as `max_completion_tokens` (default 8192). `GroqLLMClient` sends `reasoning_effort` and `include_reasoning=False` unless `LLM_REASONING_EFFORT=none`, which you must set when switching to a non-reasoning model. An output that hits the limit (`finish_reason == "length"`) logs a warning. The app is deployed on Streamlit Community Cloud from `requirements.txt` at the repo root. The git remote is `github.com/Fastpacer/Career-Portfolio-Intelligence-Agent`.

The current goal is **productionization**. Work through the [Remediation plan](#remediation-plan) in phase order. To build new capabilities, use the `feature-development` skill (`.claude/skills/feature-development/`).

## Commands

The local virtualenv sits **outside** the repo, at `D:\Career_Portfolio_Intelligence_Agent\env` (Python 3.14). From the repo root, call it as `../env/Scripts/python.exe -m <tool>`. Run every command from the repo root: `.env` is resolved relative to the current directory, and pytest's `pythonpath` expects it.

```bash
pip install -e ".[dev]"                       # package + api + ui + dev tools
pytest                                        # all tests (offline, no API key needed)
pytest tests/test_api.py::test_root           # single test
ruff check . && ruff format .                 # lint + format (CI runs `ruff format --check`)
streamlit run streamlit_app/app.py            # UI → :8501
python -m api                                 # API with reload → 127.0.0.1:8000 (or: uvicorn api.main:app)
```

Configuration lives in `.env` at the repo root (see `.env.example` for every key; only `GROQ_API_KEY` is required). On Streamlit Cloud it lives in the app's Secrets. `streamlit_app/app.py` copies top-level `st.secrets` into `os.environ`, so `career_agent.config` never imports Streamlit.

Dependencies: version ranges live in `pyproject.toml`. `requirements.txt` holds the exact pins that Streamlit Cloud installs; its final `.` line installs the package itself. When you change a dependency, update both. CI (`.github/workflows/ci.yml`) runs on Python 3.11, 3.12 and 3.13, and also checks that `requirements.txt` installs and imports.

## Architecture

```
src/career_agent/        core library: the only place business logic lives
  config.py              Settings (pydantic-settings) + get_settings(): the only reader of env/.env
  logging.py             configure_logging() (called by entry points only) + re-exported loguru `logger`
  schemas.py             CareerRequest, GitHubProfile/RepoSummary, CareerReport
  clients/llm.py         LLMClient Protocol, GroqLLMClient, get_llm_client()
  clients/github.py      GitHubClient Protocol, RestGitHubClient, get_github_client()
  core/prompts.py        versioned prompt templates (CAREER_STRATEGY_V1)
  core/pipeline.py       build_prompt() + analyze_profile(...) -> CareerReport
  parsing/cv.py          extract_cv_text(path | file-like)
api/main.py              FastAPI adapter; `python -m api` runs the dev server
streamlit_app/app.py     Streamlit adapter
tests/                   pytest; conftest has FakeLLM, FakeGitHub, make_pdf()
```

Key design rules (already in place, so keep them):
- **Both front ends call `analyze_profile` in-process.** Streamlit never calls the HTTP API, because Streamlit Cloud can't host a sidecar. FastAPI is the headless/public interface.
- **No side effects at import time.** Clients are built lazily by `lru_cache`d `get_*()` factories. A missing key raises `LLMConfigError` only when the client is built, and the API maps that to a 503. Tests check this in a subprocess.
- **Dependency injection:** `analyze_profile(..., llm=, github=)` accepts fakes. The API wires clients via `Depends(get_llm_client)` and `Depends(get_github_client)`; tests use `app.dependency_overrides`.
- Tests must not touch the network or a real `.env`. The autouse fixture in `conftest.py` switches to a temp directory, clears the env keys, and clears the `get_*` caches. Mock GitHub HTTP with `responses`.
- `career_agent.logging` shadows the stdlib name only inside the package (absolute imports keep this safe). Import `logger` from it, and don't call `logger.add` in library code.
- The `/analyze` response shape `{"career_strategy": str}` is kept for backward compatibility.

## Inconsistencies observed

Status: ✅ fixed · ⏳ open (phase noted)

| ID | Inconsistency | Status |
|----|---------------|--------|
| I-1 | Two incompatible import roots (`backend.app.*` vs `app.*`). FastAPI failed with `ModuleNotFoundError`. | ✅ P1: single `career_agent` package |
| I-2 | The README showed Streamlit → HTTP → FastAPI, but Streamlit imported the agent directly. | ✅ P1: decision documented and README rewritten |
| I-3 | Dead `cv_analyzer`/`github_analyzer`. The latter treated a dict as a list; the former hard-coded "AI/ML roles". | ✅ P1: deleted |
| I-4 | `.env` loaded three different ways; `GITHUB_API_URL` read before any load. | ✅ P1: `Settings` only |
| I-5 | Import-time side effects: a missing key crashed on import; `app.log` written to the current directory. | ✅ P1 |
| I-6 | Invalid `MODEL_NAME=moonshot` in the README, empty `.env.example`, README duplicated and stale. | ✅ P1 (full docs polish in P4) |
| I-7 | GitHub: first page only, stats from the top 5 only, no token, errors swallowed so the prompt gets `None`. | ⏳ P2 (a 10 s timeout was added in P1) |
| I-8 | `max_tokens=1200` truncated the report; scores are unparseable prose. | ⏳ P2 (token budget fixed: 8192 default, truncation logged; structured output still open) |
| I-9 | CORS `*` with credentials, no auth, rate limit or input limits, sync handlers, no `/health`. | ⏳ P3 |
| I-10 | Prompt injection via CV, repo descriptions and role; unvalidated username in the URL. | ⏳ P3 / P2 |
| I-11 | The UI shows raw tracebacks, has no caching, and gives no scanned-PDF warning. | ⏳ P2 (page separators fixed in P1) |
| I-12 | Unpinned dependencies, no packaging, tests, lint or CI; `.gitignore` blocked `.streamlit/` and fixtures. | ✅ P1 |

## Remediation plan

Work through the phases in order. Each phase should leave both entry points working and the tests green.

### Phase 1: Structure and tooling ✅ done (2026-11-01)

What landed:
- the package layout above
- `Settings`
- lazy clients
- entry-point logging
- deletion of `backend/` and the dead analyzers
- `pyproject.toml`
- pinned `requirements.txt`
- ruff and pytest (18 tests)
- pre-commit
- the CI workflow
- `.gitignore` and `.env.example` fixes
- a rewritten README

Behaviour of the analysis itself is unchanged on purpose.

### Phase 2: Correctness and resilience (fixes I-7, I-8, I-11)

1. GitHub client:
   - Read an optional `GITHUB_TOKEN`.
   - Paginate with `per_page=100`.
   - Validate the username against `^[A-Za-z0-9-]{1,39}$`.
   - Exclude forks from the scoring.
   - Compute stats over all owned repos.
   - Raise typed errors (`UserNotFound`, `RateLimited`) so the UI can show what went wrong.
2. LLM client: add retries with exponential backoff (tenacity) and a request timeout. Token usage is already logged. Use Groq `json_schema` structured outputs, which gpt-oss supports, for step 3.
3. Structured output: have the LLM return JSON that validates against an expanded `CareerReport` (scores as ints from 0 to 100, plus typed sections). Retry once on a parse failure. Render the Markdown from the model. Keep `/analyze` backward compatible or version it.
4. CV parsing:
   - Enforce maximum file size and page count.
   - If the extracted text is under about 200 characters, warn that the PDF may be scanned or image-only.
   - Replace the blind `cv_max_chars` cut with token-aware truncation.
5. UI: catch the typed errors and show friendly messages, replacing `st.exception`. Cache results with `st.cache_data` keyed on a hash of the inputs.

### Phase 3: Security and API hardening (fixes I-9, I-10)

1. Restrict CORS with an `ALLOWED_ORIGINS` setting and drop `allow_credentials`. The TODO is in `api/main.py`.
2. Use API-key auth via a header dependency, plus rate limiting (slowapi).
3. Set request size limits: cap `CareerRequest` with field constraints.
4. Make the handlers `async` (httpx and the async Groq client) or move the work off the event loop. Add `GET /health` and `response_model`, and map the typed errors to 4xx/5xx statuses.
5. Wrap each untrusted input in delimiters (`<cv>…</cv>`, `<repos>…</repos>`) and add a system message telling the model to treat their contents as data.
6. Add an option to redact emails and phone numbers from the CV before sending it to the LLM.

### Phase 4: Delivery and operations

1. Add a Dockerfile for the API (slim base, non-root user, `uvicorn --workers`) and docker-compose for local runs.
2. Use structured JSON logs with a request id. Record latency and token cost for each analysis.
3. Add `.streamlit/config.toml` and polish the docs.

## Feature development

New user-facing capabilities go in `.claude/skills/feature-development/`:
- `SKILL.md`: the workflow, the placement rules, and the definition of done.
- `features.md`: the prioritized backlog (F-1 to F-10), with a design sketch for each item.

Many features depend on the structured `CareerReport` from Phase 2.
