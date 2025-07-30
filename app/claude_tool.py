import os
import anthropic
from morvo_python.app.state import ConversationState
from morvo_python.app.prompts import MORVO_SYSTEM_PROMPT

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key == "your-api-key-here":
    # For development/testing, return mock responses if no valid API key
    def mock_ask_claude(state: ConversationState) -> str:
        return "This is a mock response. Please set a valid ANTHROPIC_API_KEY to get real responses."
    ask_claude = mock_ask_claude
else:
    client = anthropic.Anthropic(api_key=api_key)

def ask_claude(state: ConversationState) -> str:
    # Only call Claude if there's actual input
    if not state.get("input"):
        return "I'm ready to help! What would you like to know?"
        
    prompt = build_prompt(state)
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # Using the fastest model
        max_tokens=300,
        temperature=0.7,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text

def build_prompt(state: ConversationState) -> str:
    name = state.get("name", "friend")
    role = state.get("role", "")
    goal = state.get("goal", "")
    history = "\n".join(state.get("history", []))

    return f"""{MORVO_SYSTEM_PROMPT}

User name: {name}
Role: {role}
Goal: {goal}

Conversation history:
{history}
"""
