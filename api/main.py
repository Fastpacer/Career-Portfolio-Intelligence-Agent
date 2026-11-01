"""FastAPI adapter over `career_agent.core`. Run from the repo root: `uvicorn api.main:app`."""

from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from career_agent.clients.github import GitHubClient, get_github_client
from career_agent.clients.llm import LLMClient, LLMConfigError, get_llm_client
from career_agent.core.pipeline import analyze_profile
from career_agent.logging import configure_logging, logger
from career_agent.schemas import CareerRequest

configure_logging()

app = FastAPI(
    title="Career Portfolio Intelligence Agent",
    description="AI agent for career improvement insights",
)

# TODO(Phase 3, I-9): restrict origins via settings and drop allow_credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(LLMConfigError)
def _llm_not_configured(_: Request, exc: LLMConfigError) -> JSONResponse:
    logger.error("LLM not configured: {}", exc)
    return JSONResponse(status_code=503, content={"detail": "LLM backend is not configured"})


@app.get("/")
def root():
    return {"message": "Career AI Agent Running"}


@app.post("/analyze")
def analyze(
    data: CareerRequest,
    llm: Annotated[LLMClient, Depends(get_llm_client)],
    github: Annotated[GitHubClient, Depends(get_github_client)],
):
    report = analyze_profile(
        data.cv_text, data.github_username, data.target_role, llm=llm, github=github
    )
    # Response key kept for backward compatibility with the pre-refactor API.
    return {"career_strategy": report.markdown}
