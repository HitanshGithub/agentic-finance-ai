from gemini_llm import gemini

class FraudAgent:
    def run(self, expenses):
        prompt = f"""
Detect anomalies or possible fraud in the transactions below.
Explain clearly.

Transactions:
{expenses}
"""
        return gemini(prompt)
