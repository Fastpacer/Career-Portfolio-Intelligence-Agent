from fastapi import FastAPI
from app.models.request_models import CareerRequest
from app.agents.career_agent import generate_career_strategy
from app.utils.logger import get_logger
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logger = get_logger()

app = FastAPI(
    title="Career Portfolio Intelligence Agent",
    description="AI agent for career improvement insights",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Career AI Agent Running"}


@app.post("/analyze")
def analyze_profile(data: CareerRequest):

    logger.info("Starting career analysis")

    result = generate_career_strategy(
        data.cv_text,
        data.github_username,
        data.target_role
    )

    return {"career_strategy": result}