from typing import Dict, Optional

class PromptBuilder:
    @staticmethod
    def build_system_prompt(state: Dict) -> str:
        """Build system prompt based on user state."""
        # Default English prompt
        prompt = (
            "You are MORVO, an expert AI marketing strategist focused on ROI and data-driven growth. "
            "\n\nApproach:\n"
            "1. Always think strategically about the user's specific context and goals\n"
            "2. Focus on measurable outcomes and ROI potential\n"
            "3. Provide actionable, prioritized recommendations\n"
            "4. Include relevant metrics and KPIs to track success\n"
            "5. Consider budget implications and resource requirements\n"
            "\n\nResponse Format:\n"
            "- Use clear sections with emojis (📊 Strategy, 💰 ROI, ⚡️ Actions, 📈 Metrics)\n"
            "- Include bullet points for clarity\n"
            "- Highlight key insights and priorities\n"
            "- End with next steps\n\n"
        )
        
        # Add user context if available
        context = []
        if state.get("name"):
            context.append(f"The user is {state['name']}")
        if state.get("role"):
            context.append(f"a {state['role']}")
        if state.get("goal"):
            context.append(f"Their business goal is: {state['goal']}")
            
        if context:
            prompt += " ".join(context) + "\n\n"
            
        # Arabic version if needed
        if state.get("language") == "ar":
            prompt = (
                "أنت MORVO، استراتيجي تسويق ذكي وواثق. "
                "قم بالرد بطريقة واضحة واستراتيجية مع التركيز على العائد على الاستثمار والخطوات القابلة للتنفيذ. "
                "قم بتنسيق إجاباتك بأقسام واضحة ونقاط ورموز تعبيرية عند الحاجة.\n\n"
            )
            if context:
                # Add Arabic context (you may want to translate these dynamically)
                prompt += "المستخدم هو " + " و".join(context) + "\n\n"
        
        return prompt
    
    @staticmethod
    def build_morvo_prompt(state: Dict, user_input: str) -> Dict:
        """Build the full prompt for Perplexity API."""
        messages = []
        
        # Add system prompt
        system_prompt = PromptBuilder.build_system_prompt(state)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return {
            "messages": messages,
            "model": "sonar"  # Using Sonar model for its search capabilities
        }