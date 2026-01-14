from gemini_llm import gemini

class ExpenseAgent:
    def run(self, expenses):
        prompt = f"""
You are a financial analyst.

Analyze these expenses and return:
1. Total spending
2. Category-wise breakdown
3. Key insights

Expenses:
{expenses}
"""
        return gemini(prompt)
