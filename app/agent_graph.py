from langgraph.graph import StateGraph
from .state import ConversationState
from .nodes import router, chat_node
from .onboarding import onboarding_node

def get_agent_graph():
    """Create the MORVO agent graph."""
    # Initialize graph with state schema
    graph = StateGraph(ConversationState)
    
    # Add nodes
    graph.add_node("router", router)
    graph.add_node("onboarding", onboarding_node)
    graph.add_node("chat", chat_node)
    
    # Add edges
    graph.set_entry_point("router")
    graph.add_edge("router", "onboarding")
    graph.add_edge("router", "chat")
    graph.add_edge("onboarding", "router")
    graph.add_edge("chat", "router")
    
    return graph.compile()