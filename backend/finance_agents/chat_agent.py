"""
Chat Agent with LangChain Tool Calling
Uses LangChain to allow the LLM to call tools for real-time data
"""

from datetime import datetime


class ChatAgent:
    """
    AI Chat Assistant that uses LangChain tool calling.
    The LLM can call tools to fetch real-time market data.
    """
    
    def __init__(self):
        self.conversation_history = []
        self._agent = None
    
    def _get_agent(self):
        """Lazy load the LangChain agent."""
        if self._agent is None:
            try:
                from tool_agent import ask_financial_agent
                self._agent = ask_financial_agent
            except ImportError as e:
                print(f"LangChain tool agent not available: {e}")
                self._agent = self._fallback_response
        return self._agent
    
    def _fallback_response(self, message: str, context: dict = None) -> str:
        """Fallback if LangChain is not available."""
        from gemini_llm import gemini
        return gemini(message)
    
    def chat(self, message: str, context: dict = None) -> str:
        """
        Process a chat message using LangChain agent with tools.
        The agent can call tools to fetch real-time data.
        
        Args:
            message: User's question
            context: { income, expenses, goals }
        """
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            # Use LangChain agent with tool calling
            agent_func = self._get_agent()
            response = agent_func(message, context)
        except Exception as e:
            # Fallback to basic Gemini
            from gemini_llm import gemini
            context_str = self._build_context(context or {})
            prompt = f"""Today's date: {datetime.now().strftime('%Y-%m-%d')}

{context_str}

Question: {message}

Answer concisely (under 100 words):"""
            response = gemini(prompt)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _build_context(self, context: dict) -> str:
        """Build context string from user data."""
        parts = ["USER'S FINANCIAL CONTEXT:"]
        
        if context.get("income"):
            parts.append(f"- Monthly Income: ₹{context['income']}")
        
        if context.get("expenses"):
            total = sum(e.get("amount", 0) for e in context["expenses"])
            parts.append(f"- Total Expenses: ₹{total}")
        
        if context.get("goals"):
             # Format goals nicely
            goals_str = ", ".join([
                f"{g.get('name', 'Goal')} (Target: ₹{g.get('target', 0)})" 
                for g in context["goals"][:3]
            ])
            parts.append(f"- Savings Goals: {goals_str}")
        
        return "\n".join(parts) if len(parts) > 1 else "No financial context available."
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

