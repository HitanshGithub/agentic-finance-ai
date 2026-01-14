from gemini_llm import gemini, gemini_with_search


class InvestmentAgent:
    """Investment advisor that uses real-time market data."""
    
    def run(self, profile, budget_report):
        # First, fetch current market data using Google Search
        market_data = self._get_market_context()
        
        prompt = f"""You are an investment advisor with access to current market data.

CURRENT MARKET DATA (from real-time search):
{market_data}

---

USER PROFILE: {profile}

BUDGET REPORT:
{budget_report}

Based on the CURRENT market conditions above, provide:
1. Investment allocation recommendations
2. Risk assessment based on current market volatility
3. Short-term opportunities (next 3-6 months)
4. Long-term strategy (1-5 years)

Be specific and reference current market conditions in your advice.
Keep response under 250 words."""

        return gemini(prompt)
    
    def _get_market_context(self) -> str:
        """Fetch current market information using Google Search."""
        try:
            search_query = """Current stock market performance, S&P 500 trends, 
            interest rates, inflation rate, top performing sectors, 
            investment opportunities January 2025"""
            
            return gemini_with_search(f"Summarize current market conditions: {search_query}")
        except Exception as e:
            return f"[Market data unavailable: {e}]"
