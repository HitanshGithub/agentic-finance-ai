from gemini_llm import gemini

class FraudAgent:
    def run(self, expenses):
        # Format expenses in a readable way instead of raw JSON
        formatted_expenses = "\n".join([
            f"• {exp.get('category', 'Unknown')}: ₹{exp.get('amount', 0):,}" 
            for exp in expenses
        ])
        
        prompt = f"""You are a financial fraud detection expert. Analyze the following transactions for anomalies or potential fraud.

**Transactions to analyze:**
{formatted_expenses}

**Your task:**
1. Identify any suspicious transactions
2. Explain why each flagged transaction is concerning
3. Provide actionable recommendations

**Important formatting rules:**
- Do NOT output any JSON, code, or technical data structures
- Write in clear, human-readable sentences
- Use bullet points for clarity
- Mention specific amounts with the ₹ symbol
- If a transaction seems suspicious, explain in plain English why

**Example of good output:**
"The **Food** expense of **₹1,000** is unusually high compared to typical grocery spending. This could indicate:
- A large gathering or event
- Possible unauthorized use of payment method
- A data entry error

**Recommendation:** Review this transaction and verify it was authorized."

Now analyze the transactions above:
"""
        return gemini(prompt)
