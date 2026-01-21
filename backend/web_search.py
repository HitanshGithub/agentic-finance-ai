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
    """Fetch current gold prices - scrapes from Indian websites."""
    
    # Method 1: Scrape from GoodReturns (India gold prices)
    try:
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(
            "https://www.goodreturns.in/gold-rates/",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find gold price elements
            # GoodReturns shows price in format like "₹7,XXX" per gram
            price_elements = soup.find_all(['span', 'div', 'td'], string=lambda t: t and '₹' in t and ',' in t)
            
            for elem in price_elements:
                text = elem.get_text().strip()
                if '₹' in text and ',' in text:
                    # Extract price - this is likely per gram, multiply by 10 for 10g
                    import re
                    numbers = re.findall(r'[\d,]+', text)
                    if numbers:
                        price_str = numbers[0].replace(',', '')
                        if len(price_str) >= 4:  # Valid price
                            price = int(price_str)
                            # If price is per gram (around 7000-8000), multiply by 10
                            if price < 20000:
                                price = price * 10
                            return f"Gold (India): ₹{price:,}/10g (24K) - {datetime.now().strftime('%Y-%m-%d')}"
    except ImportError:
        pass  # BeautifulSoup not installed
    except Exception as e:
        print(f"GoodReturns scraping failed: {e}")
    
    # Method 2: Calculate from international gold price + INR conversion
    try:
        # Get gold price in USD
        gold_response = requests.get(
            "https://api.metals.live/v1/spot",
            timeout=10
        )
        
        # Get USD/INR rate
        forex_response = requests.get(
            "https://api.exchangerate.host/latest?base=USD&symbols=INR",
            timeout=10
        )
        
        if gold_response.status_code == 200 and forex_response.status_code == 200:
            gold_data = gold_response.json()
            forex_data = forex_response.json()
            
            usd_inr = forex_data.get('rates', {}).get('INR', 83)  # Default ~83
            
            for metal in gold_data:
                if metal.get('name', '').lower() == 'gold':
                    price_usd_oz = metal.get('price', 0)
                    # Convert: 1 oz = 31.1g, so per 10g
                    price_inr_10g = (price_usd_oz / 31.1) * 10 * usd_inr
                    return f"Gold (India est.): ₹{price_inr_10g:,.0f}/10g (24K) - {datetime.now().strftime('%Y-%m-%d')}"
    except Exception as e:
        print(f"International gold conversion failed: {e}")
    
    # Method 3: Use a simple estimate (if all else fails)
    # Current gold is around ₹7,200/gram in Jan 2026
    return f"Gold (India): ~₹72,000-75,000/10g (24K estimate) - Check goodreturns.in for exact price"


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
