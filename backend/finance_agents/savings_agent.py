from gemini_llm import gemini


class SavingsGoalAgent:
    """AI agent that provides personalized savings suggestions."""
    
    def get_suggestions(self, goal: dict, income: float = 0, expenses: list = None) -> str:
        """
        Get AI-powered suggestions for reaching a savings goal faster.
        
        Args:
            goal: { name, target, current, deadline }
            income: Monthly income
            expenses: List of expenses [{ category, amount }]
        """
        remaining = goal.get("target", 0) - goal.get("current", 0)
        progress_pct = (goal.get("current", 0) / goal.get("target", 1)) * 100
        
        expense_summary = ""
        if expenses:
            expense_summary = ", ".join([f"{e['category']}: ₹{e['amount']}" for e in expenses[:5]])
        
        prompt = f"""You are a personal finance advisor for an Indian user. A user wants to save for: {goal.get('name', 'their goal')}

Goal Details:
- Target Amount: ₹{goal.get('target', 0)}
- Current Savings: ₹{goal.get('current', 0)} ({progress_pct:.1f}% complete)
- Remaining: ₹{remaining}
- Deadline: {goal.get('deadline', 'Not set')}

User's Monthly Income: ₹{income}
Top Expenses: {expense_summary or 'Not provided'}

Provide 3-4 specific, actionable tips to help them reach this goal faster. Be encouraging and practical.
IMPORTANT: All monetary values are in Indian Rupees (₹). Do NOT mention Dollars ($).
Keep response under 150 words."""

        return gemini(prompt)
    
    def analyze_goal_feasibility(self, goal: dict, monthly_savings: float) -> dict:
        """Check if goal is achievable with current savings rate."""
        remaining = goal.get("target", 0) - goal.get("current", 0)
        
        if monthly_savings <= 0:
            months_needed = float('inf')
        else:
            months_needed = remaining / monthly_savings
        
        return {
            "remaining": remaining,
            "monthly_savings": monthly_savings,
            "months_needed": months_needed if months_needed != float('inf') else "N/A",
            "feasible": months_needed < 24  # Consider feasible if < 2 years
        }
