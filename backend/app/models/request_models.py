from pydantic import BaseModel


class CareerRequest(BaseModel):

    cv_text: str
    github_username: str
    target_role: str