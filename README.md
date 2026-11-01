# Career Portfolio Intelligence Agent

An AI-powered career analysis tool that evaluates a candidate's **CV, GitHub portfolio, and target role** to generate actionable career improvement insights: profile scores, skill gaps, portfolio feedback, resume improvements, and a 30-day learning roadmap.

## Features

- CV analysis from uploaded **PDF resumes**
- GitHub portfolio evaluation
- Role-agnostic career recommendations
- Structured career strategy output with readiness scores
- Automated 30-day learning roadmap
- Streamlit dashboard and a FastAPI HTTP API

## Architecture

```
Streamlit UI (streamlit_app/)      FastAPI (api/)  POST /analyze
            \                       /
             \                     /
          career_agent.core.pipeline.analyze_profile   (src/career_agent/)
             |                     |
     GitHub REST API          Groq LLM (default: openai/gpt-oss-120b)
```

Both front ends are thin adapters that call the same core library in-process.

## Setup

```bash
git clone https://github.com/Fastpacer/Career-Portfolio-Intelligence-Agent.git
cd Career-Portfolio-Intelligence-Agent

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

pip install -e ".[dev]"        # app + API + UI + test/lint tooling
cp .env.example .env           # then set GROQ_API_KEY
```

### Configuration

`.env` lives in the repo root and is found regardless of the directory you launch from. Only `GROQ_API_KEY` is required; see `.env.example` for all options.

- `MODEL_NAME`: defaults to `openai/gpt-oss-120b`, a reasoning model.
- `LLM_REASONING_EFFORT`: `low` | `medium` (default) | `high`. Set it to `none` if you switch to a non-reasoning model.
- `LLM_MAX_TOKENS`: defaults to 8192. It must cover hidden reasoning plus the report. A truncation warning is logged if the budget is hit.

If the key is missing, the UI shows a configuration message and the API returns `503`.

## Running

```bash
streamlit run streamlit_app/app.py      # UI  → http://localhost:8501
python -m api                           # API → http://127.0.0.1:8000 (docs at /docs)
```

## Development

```bash
pytest                                   # all tests (no network or API key needed)
pytest tests/test_api.py::test_root      # single test
ruff check . && ruff format .            # lint + format
pre-commit install                       # optional git hooks
```

## Deployment (Streamlit Community Cloud)

Main file: `streamlit_app/app.py`. Cloud installs from `requirements.txt` (pinned, and installs this package via `.`). Add `GROQ_API_KEY` under the app's **Secrets**.

## Tech Stack

FastAPI · Streamlit · Groq · GitHub REST API · pdfplumber · pydantic-settings · loguru

## License

MIT
