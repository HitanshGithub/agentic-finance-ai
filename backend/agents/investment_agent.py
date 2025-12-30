from gemini_llm import gemini

class InvestmentAgent:
    def run(self, profile, budget_report):
        prompt = f"""
You are an investment advisor.

User profile:
{profile}

Budget report:
{budget_report}

Suggest:
- Investment allocation
- Risk level
- Short & long-term plan
"""
        return gemini(prompt)
