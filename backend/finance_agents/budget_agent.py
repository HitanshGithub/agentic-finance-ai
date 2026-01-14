from gemini_llm import gemini

class BudgetAgent:
    def run(self, income, expense_report):
        prompt = f"""
You are a budget planning expert.

Income: {income}

Expense report:
{expense_report}

Provide:
- Budget health
- Savings recommendation
- Spending reduction tips
"""
        return gemini(prompt)
