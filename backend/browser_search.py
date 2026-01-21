"""
Browser Search Module - Uses LangChain HyperBrowser to fetch real web data
This allows fetching gold prices from Indian websites and other live data
"""

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def search_with_browser(task: str) -> str:
    """
    Use HyperBrowser to perform browser-based search and extraction.
    This actually browses websites and extracts data.
    """
    try:
        from langchain_hyperbrowser import HyperbrowserBrowserUseTool
        
        tool = HyperbrowserBrowserUseTool()
        result = tool.run({"task": task})
        return result
    except ImportError:
        return "[HyperBrowser not installed. Run: pip install langchain-hyperbrowser]"
    except Exception as e:
        return f"[Browser Error] {str(e)}"


def get_india_gold_price() -> str:
    """
    Fetch current gold prices in India by browsing financial websites.
    """
    task = """Go to https://www.goodreturns.in/gold-rates.html and:
1. Find the current 24 carat gold price per 10 grams in India
2. Find the current 22 carat gold price per 10 grams in India
3. Note the date when prices were last updated
Return the gold prices in a clear format."""

    try:
        result = search_with_browser(task)
        if result and not result.startswith("["):
            return f"[{datetime.now().strftime('%Y-%m-%d')}] India Gold Prices: {result}"
        return result
    except Exception as e:
        # Fallback: try alternate method
        return fallback_gold_price()


def fallback_gold_price() -> str:
    """Fallback method using HTTP requests if browser fails."""
    import requests
    
    try:
        # Try to scrape from a simple source
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # GoldAPI.io (free tier available)
        response = requests.get(
            "https://www.goldapi.io/api/XAU/INR",
            headers={
                "x-access-token": os.getenv("GOLD_API_KEY", ""),
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            price_per_oz = data.get('price', 0)
            # Convert oz to 10 grams (1 oz = 31.1g)
            price_per_10g = (price_per_oz / 31.1) * 10
            return f"Gold: ₹{price_per_10g:,.0f}/10g (24K, estimated from international prices)"
        
    except Exception:
        pass
    
    return "Gold price data requires browser access. Try manually checking goodreturns.in"


def get_market_news() -> str:
    """
    Get latest financial news by browsing news sites.
    """
    task = """Go to https://economictimes.indiatimes.com/markets and:
1. Find the latest 3 market headlines
2. Note the Sensex and Nifty values if visible
Return a brief summary of current market conditions."""

    return search_with_browser(task)


def search_financial_topic(query: str) -> str:
    """
    Search for any financial topic using browser.
    """
    task = f"""Search on Google for: "{query} site:moneycontrol.com OR site:economictimes.com"
Find the most relevant and recent information about: {query}
Return the key findings with dates."""

    return search_with_browser(task)


# Test
if __name__ == "__main__":
    print("Testing Browser Search...")
    print("-" * 50)
    result = get_india_gold_price()
    print(f"Gold Price Result:\n{result}")
