from gemini_llm import gemini

class ExpenseAgent:
    def run(self, expenses):
        # Format expenses in a readable way
        formatted_expenses = "\n".join([
            f"• {exp.get('category', 'Unknown')}: ₹{exp.get('amount', 0):,}" 
            for exp in expenses
        ])
        
        total = sum(exp.get('amount', 0) for exp in expenses)
        
        prompt = f"""You are a financial analyst specializing in personal expense analysis.

**Expenses to analyze:**
{formatted_expenses}

**Total Spending:** ₹{total:,}

**Your task:**
Provide a comprehensive expense analysis including:

1. **Total Spending Summary** - Total amount and what it represents
2. **Category-wise Breakdown** - Use a clear table format with Category, Amount, and Percentage
3. **Key Insights** - 3-5 important observations about spending patterns

**Formatting rules:**
- Use the ₹ symbol for all currency amounts
- Format numbers with commas (e.g., ₹10,000)
- Create a markdown table for the breakdown
- Use bullet points for insights
- Be specific and actionable

Analyze the expenses:
"""
        return gemini(prompt)
