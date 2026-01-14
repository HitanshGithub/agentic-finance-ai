from gemini_llm import gemini


class ChatAgent:
    """
    AI Chat Assistant for conversational financial questions.
    Provides contextual answers based on user's financial data.
    """
    
    def __init__(self):
        self.conversation_history = []
    
    def chat(self, message: str, context: dict = None) -> str:
        """
        Process a chat message and return AI response.
        
        Args:
            message: User's question
            context: {
                income: float,
                expenses: list,
                last_analysis: dict,
                goals: list
            }
        """
        # Build context from user data
        context_str = self._build_context(context or {})
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Keep last 5 exchanges for context
        recent_history = self.conversation_history[-10:]
        history_str = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in recent_history[:-1]  # Exclude current message
        ])
        
        prompt = f"""You are a helpful personal finance assistant. Answer the user's question based on their financial context.

{context_str}

{f"Previous conversation:{chr(10)}{history_str}" if history_str else ""}

User's Question: {message}

Provide a helpful, concise response. If you don't have enough data to answer specifically, give general financial advice. Keep response under 100 words."""

        response = gemini(prompt)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _build_context(self, context: dict) -> str:
        """Build context string from user data."""
        parts = ["USER'S FINANCIAL CONTEXT:"]
        
        if context.get("income"):
            parts.append(f"- Monthly Income: ${context['income']}")
        
        if context.get("expenses"):
            total = sum(e.get("amount", 0) for e in context["expenses"])
            parts.append(f"- Total Expenses: ${total}")
            
            # Top 3 expense categories
            sorted_exp = sorted(
                context["expenses"], 
                key=lambda x: x.get("amount", 0), 
                reverse=True
            )[:3]
            if sorted_exp:
                top_cats = ", ".join([
                    f"{e.get('category', 'Unknown')}: ${e.get('amount', 0)}" 
                    for e in sorted_exp
                ])
                parts.append(f"- Top Expenses: {top_cats}")
        
        if context.get("goals"):
            goal_names = ", ".join([g.get("name", "Goal") for g in context["goals"][:3]])
            parts.append(f"- Savings Goals: {goal_names}")
        
        if context.get("last_analysis"):
            parts.append("- Has recent financial analysis available")
        
        return "\n".join(parts) if len(parts) > 1 else "No financial context available."
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
