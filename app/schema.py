from typing_extensions import TypedDict, Optional

class UserProfileState(TypedDict, total=False):
    name: Optional[str]
    role: Optional[str]
    goal: Optional[str]
    history: list[str]
    messages: list[dict]  # Optional memory expansion
