import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.state import ChatRequest, ChatResponse
from app.supabase_client import test_supabase_connection

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MORVO - AI Marketing Assistant",
    description="A bilingual (Arabic/English) marketing strategist focused on ROI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def root():
    return {
        "message": "👋 MORVO is ready to skyrocket your ROI!",
        "docs_url": "/docs",
        "supported_languages": ["English", "Arabic (العربية)"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint."""
    try:
        # For now, just echo back the message
        return ChatResponse(response=f"Echo: {request.message}", history=[request.message])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-supabase")
def test_supabase():
    """Test endpoint to verify Supabase connection and insert a test user profile."""
    result = test_supabase_connection()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result
