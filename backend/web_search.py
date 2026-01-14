"""
Web Search Module - Fetches real-time data from the web
Uses HTTP requests to get current market data from financial APIs
"""

import requests
from datetime import datetime


def search_web(query: str) -> str:
    """
    Search the web for current information.
    Uses multiple sources for financial data.
    """
    results = []
    
    # Try to get data from multiple sources
    try:
        # 1. Try financial news/data APIs
        gold_data = get_gold_prices()
        if gold_data:
            results.append(f"GOLD PRICES: {gold_data}")
    except:
        pass
    
    try:
        # 2. Get stock market overview
        market_data = get_market_overview()
        if market_data:
            results.append(f"MARKET DATA: {market_data}")
    except:
        pass
    
    try:
        # 3. Get crypto data if relevant
        if any(word in query.lower() for word in ['crypto', 'bitcoin', 'btc', 'eth']):
            crypto_data = get_crypto_prices()
            if crypto_data:
                results.append(f"CRYPTO: {crypto_data}")
    except:
        pass
    
    if results:
        return "\n\n".join(results)
    else:
        return f"[Live data fetch attempted at {datetime.now().strftime('%Y-%m-%d %H:%M')}]"


def get_gold_prices() -> str:
    """Fetch current gold prices from public API."""
    try:
        # Using metals.live API (free, no auth required)
        response = requests.get(
            "https://api.metals.live/v1/spot",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            # Find gold in the response
            for metal in data:
                if metal.get('name', '').lower() == 'gold':
                    price_usd = metal.get('price', 'N/A')
                    return f"Gold: ${price_usd}/oz (USD) - Updated: {datetime.now().strftime('%Y-%m-%d')}"
    except Exception as e:
        pass
    
    # Fallback: try alternative API
    try:
        response = requests.get(
            "https://api.exchangerate.host/latest?base=XAU",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('rates', {}).get('USD'):
                usd_per_oz = 1 / data['rates']['USD']
                return f"Gold: ~${usd_per_oz:.2f}/oz (estimated)"
    except:
        pass
    
    return None


def get_market_overview() -> str:
    """Get stock market overview data."""
    try:
        # Using a public financial data endpoint
        # Note: For production, use a proper API like Alpha Vantage, Yahoo Finance, etc.
        
        # Try Yahoo Finance API (unofficial but works)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        indices = []
        
        # Fetch S&P 500 data
        try:
            response = requests.get(
                "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=1d",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get('chart', {}).get('result', [{}])[0]
                meta = result.get('meta', {})
                price = meta.get('regularMarketPrice', 'N/A')
                prev_close = meta.get('previousClose', 0)
                change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                indices.append(f"S&P 500: {price:,.2f} ({change:+.2f}%)")
        except:
            pass
        
        # Fetch NASDAQ data
        try:
            response = requests.get(
                "https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?interval=1d&range=1d",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get('chart', {}).get('result', [{}])[0]
                meta = result.get('meta', {})
                price = meta.get('regularMarketPrice', 'N/A')
                prev_close = meta.get('previousClose', 0)
                change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                indices.append(f"NASDAQ: {price:,.2f} ({change:+.2f}%)")
        except:
            pass
        
        if indices:
            return f"US Markets ({datetime.now().strftime('%Y-%m-%d')}): " + " | ".join(indices)
    except:
        pass
    
    return None


def get_crypto_prices() -> str:
    """Fetch cryptocurrency prices."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            btc = data.get('bitcoin', {})
            eth = data.get('ethereum', {})
            
            parts = []
            if btc:
                btc_price = btc.get('usd', 'N/A')
                btc_change = btc.get('usd_24h_change', 0)
                parts.append(f"BTC: ${btc_price:,.0f} ({btc_change:+.1f}%)")
            if eth:
                eth_price = eth.get('usd', 'N/A')
                eth_change = eth.get('usd_24h_change', 0)
                parts.append(f"ETH: ${eth_price:,.0f} ({eth_change:+.1f}%)")
            
            if parts:
                return " | ".join(parts)
    except:
        pass
    
    return None


def get_interest_rates() -> str:
    """Fetch current interest rate information."""
    # Note: Federal Reserve rates typically need to be scraped from FRED API
    # For now, return placeholder - in production use FRED API
    return "Check Federal Reserve website for current rates"


def fetch_financial_context(query: str = "") -> dict:
    """
    Fetch comprehensive financial context for investment advice.
    Returns a dictionary with various market data.
    """
    context = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market_data": get_market_overview(),
        "gold": get_gold_prices(),
        "crypto": get_crypto_prices() if 'crypto' in query.lower() else None,
    }
    
    # Build summary
    summary_parts = [f"Data fetched at: {context['timestamp']}"]
    
    if context['market_data']:
        summary_parts.append(context['market_data'])
    if context['gold']:
        summary_parts.append(context['gold'])
    if context['crypto']:
        summary_parts.append(context['crypto'])
    
    context['summary'] = "\n".join(summary_parts)
    
    return context
