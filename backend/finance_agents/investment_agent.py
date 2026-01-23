from gemini_llm import gemini, get_live_market_data


class InvestmentAgent:
    """Investment advisor that uses REAL-TIME market data from HTTP APIs."""
    
    def run(self, profile, budget_report):
        # Fetch REAL current market data using HTTP requests
        market_data = self._get_real_market_data()
        
        prompt = f"""You are an investment advisor with access to REAL current market data.

LIVE MARKET DATA (fetched via HTTP just now):
{market_data}

---

USER PROFILE: {profile}

BUDGET REPORT:
{budget_report}

Based on the ACTUAL LIVE market data above, provide:
1. Investment allocation recommendations with specific percentages
2. Risk assessment referencing current market volatility from the data
3. Short-term opportunities (next 3-6 months) based on current trends
4. Long-term strategy (1-5 years)

IMPORTANT: 
- Reference the actual numbers from the live data in your response.
- All investment values should be in Indian Rupees (₹).
Keep response under 300 words."""

        return gemini(prompt)
    
    def _get_real_market_data(self) -> str:
        """Fetch REAL market data using HTTP requests to APIs."""
        try:
            return get_live_market_data()
        except Exception as e:
            return f"[Market data fetch error: {e}]"

