from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserProfile(BaseModel):
    """User profile data model."""
    name: str
    role: str
    goal: str
    language: str = Field(default="en")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ChatMessage(BaseModel):
    """Chat message data model."""
    role: str = Field(enum=["user", "assistant", "system"])
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Chat API request model."""
    message: str
    user_id: str

class ChatResponse(BaseModel):
    """Chat API response model."""
    message: str
    history: List[ChatMessage]