from typing import Dict, Optional, List
from datetime import datetime

class TemporaryMemory:
    """Temporary in-memory storage until Supabase is ready."""
    
    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._conversations: Dict[str, List[Dict]] = {}
    
    def save_user_profile(self, user_id: str, profile: Dict) -> None:
        """Save or update user profile."""
        if user_id not in self._users:
            profile["created_at"] = datetime.utcnow().isoformat()
        profile["updated_at"] = datetime.utcnow().isoformat()
        self._users[user_id] = profile
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID."""
        return self._users.get(user_id)
    
    def save_conversation(self, user_id: str, message: Dict) -> None:
        """Save a conversation message."""
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        message["timestamp"] = datetime.utcnow().isoformat()
        self._conversations[user_id].append(message)
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history."""
        history = self._conversations.get(user_id, [])
        return history[-limit:] if limit else history
    
    def update_user_field(self, user_id: str, field: str, value: str) -> None:
        """Update a specific field in user profile."""
        if user_id in self._users:
            self._users[user_id][field] = value
            self._users[user_id]["updated_at"] = datetime.utcnow().isoformat()

# Global instance for temporary storage
memory = TemporaryMemory()