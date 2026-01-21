from gemini_llm import gemini

class BudgetAgent:
    def run(self, income, expense_report):
        prompt = f"""You are a budget planning expert helping users optimize their finances.

**Monthly Income:** ₹{income:,}

**Expense Analysis:**
{expense_report}

**Your task:**
Provide a comprehensive budget plan including:

1. **Budget Health Assessment**
   - Is the user in surplus or deficit?
   - What percentage of income is being spent vs saved?
   - Give a health rating (Excellent/Good/Needs Improvement/Critical)

2. **Savings Recommendations**
   - Recommended savings percentage based on income
   - Suggested savings amount in ₹
   - Emergency fund recommendations

3. **Spending Reduction Tips**
   - Specific areas where spending can be reduced
   - Practical tips for each category
   - Potential savings from each recommendation

**Formatting rules:**
- Use ₹ symbol for all amounts
- Format numbers with commas (e.g., ₹10,000)
- Use clear headings with **bold** text
- Use bullet points for actionable items
- Be specific with amounts and percentages

Provide the budget plan:
"""
        return gemini(prompt)
