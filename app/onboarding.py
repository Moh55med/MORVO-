from typing import Dict
from datetime import datetime
from .state import ConversationState
from .memory import memory
from .models import UserProfile, ChatMessage

def detect_language(text: str) -> str:
    """Simple language detection - returns 'ar' if Arabic characters found, else 'en'."""
    # Unicode ranges for Arabic characters
    arabic_ranges = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)]
    
    for char in text:
        code = ord(char)
        if any(start <= code <= end for start, end in arabic_ranges):
            return "ar"
    return "en"

def get_onboarding_message(state: ConversationState, lang: str) -> str:
    """Get the appropriate onboarding message based on state."""
    messages = {
        "name": {
            "en": "👋 Hi! I'm MORVO, your AI marketing strategist. What's your name?",
            "ar": "👋 مرحباً! أنا MORVO، مستشارك التسويقي الذكي. ما اسمك؟"
        },
        "role": {
            "en": f"👔 Nice to meet you, {state['name']}! What's your role or title?",
            "ar": f"👔 سعيد بلقائك يا {state['name']}! ما هو دورك أو منصبك؟"
        },
        "goal": {
            "en": "🎯 What's your main business or marketing goal?",
            "ar": "🎯 ما هو هدفك الرئيسي في العمل أو التسويق؟"
        },
        "complete": {
            "en": f"✨ Perfect! I'm ready to help you achieve your goals, {state['name']}!",
            "ar": f"✨ ممتاز! أنا جاهز لمساعدتك في تحقيق أهدافك يا {state['name']}!"
        }
    }
    
    if not state.get("name"):
        return messages["name"][lang]
    elif not state.get("role"):
        return messages["role"][lang]
    elif not state.get("goal"):
        return messages["goal"][lang]
    else:
        return messages["complete"][lang]

def onboarding_node(state: ConversationState) -> Dict:
    """Handle user onboarding flow."""
    user_input = state.get("input", "").strip()
    user_id = state.get("user_id")
    
    if not user_id:
        raise ValueError("User ID not found in state")
    
    if not user_input:
        # Load existing profile if available
        profile = memory.get_user_profile(user_id)
        if profile:
            return {
                "name": profile["name"],
                "role": profile["role"],
                "goal": profile["goal"],
                "language": profile["language"],
                "history": get_onboarding_message(profile, profile["language"])
            }
        return {"history": get_onboarding_message({}, "en")}
    
    # Detect language from user input
    lang = detect_language(user_input)
    updates = {"language": lang}
    
    # Update appropriate field based on state
    if not state.get("name"):
        updates["name"] = user_input
        updates["history"] = get_onboarding_message({"name": user_input}, lang)
        
        # Save initial profile
        profile = UserProfile(
            name=user_input,
            role="",
            goal="",
            language=lang,
            created_at=datetime.utcnow()
        )
        memory.save_user_profile(user_id, profile.dict())
        
    elif not state.get("role"):
        updates["role"] = user_input
        profile = memory.get_user_profile(user_id)
        if profile:
            profile["role"] = user_input
            memory.save_user_profile(user_id, profile)
        updates["history"] = get_onboarding_message({"name": state["name"], "role": user_input}, lang)
        
    elif not state.get("goal"):
        updates["goal"] = user_input
        profile = memory.get_user_profile(user_id)
        if profile:
            profile["goal"] = user_input
            memory.save_user_profile(user_id, profile)
        updates["history"] = get_onboarding_message({"name": state["name"], "role": state["role"], "goal": user_input}, lang)
        
    else:
        updates["history"] = get_onboarding_message(state, lang)
    
    # Save the interaction
    message = ChatMessage(
        role="assistant",
        content=updates["history"],
        timestamp=datetime.utcnow()
    )
    memory.save_conversation(user_id, message.dict())
    
    updates["input"] = ""  # Clear input after processing
    return updates