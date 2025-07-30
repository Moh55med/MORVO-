from typing import Dict
from datetime import datetime
from .state import ConversationState
from .perplexity_client import PerplexityClient
from .prompt_builder import PromptBuilder
from .memory import memory
from .models import ChatMessage, UserProfile

# Initialize Perplexity client
perplexity = PerplexityClient()

async def router(state: ConversationState) -> Dict:
    """Route to appropriate node based on state."""
    # Go to onboarding if any required field is missing
    if not state.get("name") or not state.get("role") or not state.get("goal"):
        return {"next": "onboarding"}
    return {"next": "chat"}

async def chat_node(state: ConversationState) -> Dict:
    """Handle chat interactions using Perplexity."""
    try:
        user_id = state.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in state")
            
        # Load user profile from memory
        profile = memory.get_user_profile(user_id)
        if not profile:
            profile = UserProfile(
                name=state.get("name", ""),
                role=state.get("role", ""),
                goal=state.get("goal", ""),
                language=state.get("language", "en")
            ).dict()
            memory.save_user_profile(user_id, profile)
        
        # Build prompt with user context
        prompt_data = PromptBuilder.build_morvo_prompt(profile, state.get("input", ""))
        
        # Get response from Perplexity
        response = await perplexity.chat(prompt_data["messages"])
        
        # Save conversation to memory
        user_msg = ChatMessage(
            role="user",
            content=state.get("input", ""),
            timestamp=datetime.utcnow()
        ).dict()
        assistant_msg = ChatMessage(
            role="assistant",
            content=response,
            timestamp=datetime.utcnow()
        ).dict()
        
        memory.save_conversation(user_id, user_msg)
        memory.save_conversation(user_id, assistant_msg)
        
        return {
            "history": response,
            "input": "",  # Clear input after processing
            "messages": [user_msg, assistant_msg]
        }
        
    except Exception as e:
        # Handle errors gracefully
        error_msg = "I apologize, but I encountered an error. Could you please try again?"
        if state.get("language") == "ar":
            error_msg = "عذراً، لقد واجهت خطأ. هل يمكنك المحاولة مرة أخرى؟"
        
        return {
            "history": error_msg,
            "input": ""
        }