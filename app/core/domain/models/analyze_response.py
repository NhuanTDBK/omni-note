from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    category: str
    summarization: str
    metadata: dict = None
    user_id: str = None
