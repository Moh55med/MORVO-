from typing import List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    history: List[str]