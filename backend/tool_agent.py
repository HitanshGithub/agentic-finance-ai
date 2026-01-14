"""
Tool Agent using Gemini Native Function Calling
No LangChain required - uses Google's native function calling
"""

import os
from dotenv import load_dotenv
from datetime import datetime
from web_search import (
    get_gold_prices, 
    get_market_overview, 
    get_crypto_prices,
    fetch_financial_context
)

load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ===== DEFINE TOOLS AS FUNCTIONS =====

def get_current_date() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_stock_market() -> str:
    """Get current stock market data (S&P 500, NASDAQ)."""
    result = get_market_overview()
    if result:
        return result
    return "Unable to fetch market data. Markets may be closed."


def search_gold_prices() -> str:
    """Get current gold prices from the web."""
    result = get_gold_prices()
    if result:
        return f"[{datetime.now().strftime('%Y-%m-%d')}] {result}"
    return "Gold price data temporarily unavailable."


def search_crypto_prices() -> str:
    """Get current cryptocurrency prices (Bitcoin, Ethereum)."""
    result = get_crypto_prices()
    if result:
        return result
    return "Crypto data temporarily unavailable."


def search_all_financial_data(query: str = "") -> str:
    """Get comprehensive financial data."""
    context = fetch_financial_context(query)
    return context.get('summary', 'No data available')


# Available tools
TOOLS = {
    "get_current_date": get_current_date,
    "search_stock_market": search_stock_market,
    "search_gold_prices": search_gold_prices,
    "search_crypto_prices": search_crypto_prices,
    "search_all_financial_data": search_all_financial_data,
}


def ask_agent(question: str) -> str:
    """
    Ask a question and get a response with real-time data.
    Uses a simple prompt-based tool calling approach.
    """
    # First, fetch all relevant data
    current_date = get_current_date()
    market_data = search_stock_market()
    gold_data = search_gold_prices()
    crypto_data = search_crypto_prices()
    
    # Build context with live data
    live_context = f"""LIVE DATA (fetched at {current_date}):

📈 STOCK MARKET:
{market_data}

🥇 GOLD PRICES:
{gold_data}

💰 CRYPTOCURRENCY:
{crypto_data}
"""
    
    prompt = f"""You are a financial advisor with access to REAL-TIME market data.

{live_context}

---

USER QUESTION: {question}

INSTRUCTIONS:
1. Use ONLY the live data above - do NOT use your training knowledge for prices
2. Reference the specific numbers from the live data
3. Provide helpful, actionable advice
4. Acknowledge if any data is unavailable

Your response:"""

    try:
        model = genai.GenerativeModel("models/gemma-3-27b-it")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 500
            }
        )
        return response.text
    except Exception as e:
        return f"[Agent Error] {str(e)}"


def ask_with_context(question: str, context: dict = None) -> str:
    """
    Ask the agent with user context.
    """
    context_str = ""
    if context:
        if context.get('income'):
            context_str += f"\nUser's monthly income: ${context['income']}"
        if context.get('expenses'):
            total = sum(e.get('amount', 0) for e in context['expenses'])
            context_str += f"\nUser's total expenses: ${total}"
        if context.get('goals'):
            goals = ", ".join([g.get('name', 'Goal') for g in context['goals']])
            context_str += f"\nUser's savings goals: {goals}"
    
    full_question = f"{question}\n\nUser Context:{context_str}" if context_str else question
    return ask_agent(full_question)


# Test
if __name__ == "__main__":
    print("Testing Tool Agent...")
    print("-" * 50)
    result = ask_agent("What is the current gold price and S&P 500?")
    print(result)
