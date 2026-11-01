---
name: feature-development
description: Add a new capability to the Career Portfolio Intelligence Agent. Use when building a new analysis, data source, report section, UI view or API endpoint, or when picking the next feature from the backlog in features.md.
---

# Feature development: Career Portfolio Intelligence Agent

## Before you start

1. Check that the package layout from Phase 1 of the CLAUDE.md remediation plan exists (`src/career_agent/`). If it doesn't, stop. Tell the user that Phase 1 is a prerequisite, and offer to do it first. Do not add features to the old `backend/app` layout.
2. Read `features.md` in this folder. Pick the item the user named, or recommend the highest-priority unblocked item. Check its **Depends on** line.

## Where code goes

All business logic lives in `src/career_agent/`. The front ends are thin adapters only.

| Kind of change | Location |
|---|---|
| New external data source (e.g. job board, LinkedIn export) | `clients/<source>.py`, behind a small Protocol so tests can fake it |
| New analysis step | `core/stages/<name>.py`, as a function `(ProfileContext) -> StageResult`, registered in `core/pipeline.py` |
| New prompt | `core/prompts.py`, as a named constant with a version suffix (`SKILL_GAP_V2`), never inline f-strings in stages |
| New report section or score | Add the field to `CareerReport` in `schemas.py` first, then the prompt, then the renderer |
| UI | `streamlit_app/` reads `CareerReport` fields; it never parses LLM text |
| API | `api/main.py` adds an endpoint with a `response_model`; dependencies come from `Depends` so tests can override them |
| Config | Add a field to `Settings` in `config.py`, then add it to `.env.example` and the CLAUDE.md config list |

## Conventions

- **The LLM returns structured data.** Every LLM call validates against a pydantic model, and retries once if parsing fails. Free-text Markdown is produced only by the renderer.
- **Untrusted input is fenced.** CV text, repo data, job descriptions and user-entered roles go inside XML-style tags in the prompt, and the system prompt tells the model to treat their contents as data.
- **Independent stages run concurrently** (`asyncio.gather`). The pipeline as a whole must still finish within the Streamlit request (target under 30 s).
- **Every stage degrades gracefully.** If an optional data source fails, the report still renders, with a visible "data unavailable" note. Never put `None` into the prompt.
- **Cost awareness.** Log tokens per stage. Do not add an LLM call when deterministic code can do the job, such as keyword matching, counting or date math.

## Definition of done

1. The schema, stage, prompt and renderer changes are all in place.
2. Unit tests use the fake LLM client and mocked HTTP. Cover at least one happy path and one degraded path (source down or malformed LLM JSON).
3. `ruff check .` and `pytest` pass.
4. Streamlit was checked by hand, using `streamlit run streamlit_app/app.py` with a real key.
5. `features.md` is updated (mark the item done) and so is the README feature list.
