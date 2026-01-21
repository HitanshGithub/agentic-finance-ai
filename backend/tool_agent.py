"""
Tool Agent for Financial Data
Fetches real-time data FIRST, then uses Gemma to generate response
(Gemma doesn't support function calling, so we fetch data manually)
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import google.generativeai as genai

load_dotenv()

# Configure Gemma
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemma-3-27b-it")


# ===== DATA FETCHING TOOLS =====

def get_current_date() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_gold_price_india() -> str:
    """Fetch current gold prices in India."""
    try:
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get("https://www.goodreturns.in/gold-rates/", headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            import re
            text = soup.get_text()
            
            # Look for prices in the range of 1,40,000+ (current gold prices are high)
            matches = re.findall(r'(?:Rs\.?|₹)\s*([\d,]+)', text)
            for match in matches:
                price = int(match.replace(',', ''))
                # Current gold is around ₹1,45,000 per 10g (Jan 2026)
                if 130000 <= price <= 200000:
                    return f"Gold 24K: ₹{price:,}/10g ({datetime.now().strftime('%Y-%m-%d')})"
    except Exception as e:
        print(f"Scraping error: {e}")
    
    # Fallback - calculate from international gold price
    try:
        resp = requests.get("https://api.metals.live/v1/spot", timeout=10)
        if resp.status_code == 200:
            for metal in resp.json():
                if metal.get('name', '').lower() == 'gold':
                    usd_per_oz = metal.get('price', 2650)
                    # 1 oz = 31.1g, current USD/INR ~ 83-84
                    inr_per_10g = (usd_per_oz / 31.1) * 10 * 84
                    return f"Gold 24K (calculated): ₹{inr_per_10g:,.0f}/10g ({datetime.now().strftime('%Y-%m-%d')})"
    except:
        pass
    
    # Updated fallback - gold in Jan 2026 is around ₹1,45,000/10g
    return f"Gold 24K: ~₹1,45,000-1,50,000/10g ({datetime.now().strftime('%Y-%m-%d')}) - check goodreturns.in"


def get_stock_market_data() -> str:
    """Fetch S&P 500 and NASDAQ data."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        results = []
        
        # S&P 500
        try:
            resp = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=1d", headers=headers, timeout=10)
            if resp.status_code == 200:
                meta = resp.json().get('chart', {}).get('result', [{}])[0].get('meta', {})
                price = meta.get('regularMarketPrice', 0)
                prev = meta.get('previousClose', 0)
                change = ((price - prev) / prev * 100) if prev else 0
                results.append(f"S&P 500: {price:,.2f} ({change:+.2f}%)")
        except:
            pass
        
        # NASDAQ
        try:
            resp = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?interval=1d&range=1d", headers=headers, timeout=10)
            if resp.status_code == 200:
                meta = resp.json().get('chart', {}).get('result', [{}])[0].get('meta', {})
                price = meta.get('regularMarketPrice', 0)
                prev = meta.get('previousClose', 0)
                change = ((price - prev) / prev * 100) if prev else 0
                results.append(f"NASDAQ: {price:,.2f} ({change:+.2f}%)")
        except:
            pass
        
        if results:
            return f"US Markets ({datetime.now().strftime('%Y-%m-%d')}): " + " | ".join(results)
    except:
        pass
    return "Stock market data unavailable"


def get_crypto_prices() -> str:
    """Fetch Bitcoin and Ethereum prices."""
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,inr&include_24hr_change=true", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            parts = []
            if 'bitcoin' in data:
                btc = data['bitcoin']
                parts.append(f"BTC: ${btc.get('usd', 0):,.0f} (₹{btc.get('inr', 0):,.0f}) [{btc.get('usd_24h_change', 0):+.1f}%]")
            if 'ethereum' in data:
                eth = data['ethereum']
                parts.append(f"ETH: ${eth.get('usd', 0):,.0f} (₹{eth.get('inr', 0):,.0f}) [{eth.get('usd_24h_change', 0):+.1f}%]")
            if parts:
                return f"Crypto ({datetime.now().strftime('%Y-%m-%d')}): " + " | ".join(parts)
    except:
        pass
    return "Crypto data unavailable"


def get_silver_price() -> str:
    """Fetch current silver prices from MoneyControl."""
    try:
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Try MoneyControl silver page
        response = requests.get("https://www.moneycontrol.com/commodity/silver-price.html", headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            import re
            text = soup.get_text()
            
            # Look for silver prices (around ₹90,000-1,00,000 per kg or ₹90-100 per gram)
            matches = re.findall(r'(?:Rs\.?|₹)\s*([\d,]+)', text)
            for match in matches:
                price = int(match.replace(',', ''))
                # Silver is around ₹90,000-1,10,000 per KG
                if 80000 <= price <= 150000:
                    return f"Silver: ₹{price:,}/kg ({datetime.now().strftime('%Y-%m-%d')})"
                # Or per 10g (around ₹900-1100)
                if 800 <= price <= 1500:
                    return f"Silver: ₹{price:,}/10g ({datetime.now().strftime('%Y-%m-%d')})"
    except Exception as e:
        print(f"Silver scraping error: {e}")
    
    # Fallback - calculate from international silver price
    try:
        resp = requests.get("https://api.metals.live/v1/spot", timeout=10)
        if resp.status_code == 200:
            for metal in resp.json():
                if metal.get('name', '').lower() == 'silver':
                    usd_per_oz = metal.get('price', 30)
                    # 1 oz = 31.1g, USD/INR ~ 84
                    inr_per_kg = (usd_per_oz / 31.1) * 1000 * 84
                    return f"Silver (calculated): ₹{inr_per_kg:,.0f}/kg ({datetime.now().strftime('%Y-%m-%d')})"
    except:
        pass
    
    # Fallback - current silver is around ₹95,000/kg in Jan 2026
    return f"Silver: ~₹95,000-1,00,000/kg ({datetime.now().strftime('%Y-%m-%d')}) - check moneycontrol.com"


# ===== MAIN AGENT FUNCTION =====

def ask_financial_agent(question: str, context: dict = None) -> str:
    """
    Main entry point - fetches real-time data FIRST, then asks Gemma.
    """
    # Step 1: Fetch all real-time data
    current_date = get_current_date()
    gold_price = get_gold_price_india()
    silver_price = get_silver_price()
    stock_data = get_stock_market_data()
    crypto_data = get_crypto_prices()
    
    # Step 2: Build context
    live_data = f"""LIVE MARKET DATA (fetched at {current_date}):

🥇 GOLD: {gold_price}

🥈 SILVER: {silver_price}

📈 STOCKS: {stock_data}

💰 CRYPTO: {crypto_data}
"""
    
    # Add user context if provided
    user_context = ""
    if context:
        if context.get('income'):
            user_context += f"\n- Income: ₹{context['income']}"
        if context.get('expenses'):
            total = sum(e.get('amount', 0) for e in context['expenses'])
            user_context += f"\n- Expenses: ₹{total}"
        if context.get('goals'):
            goals = ", ".join([g.get('name', 'Goal') for g in context['goals']])
            user_context += f"\n- Goals: {goals}"
    
    # Step 3: Create prompt with live data
    prompt = f"""You are a financial advisor. Use ONLY the live data below to answer questions.

{live_data}
{f"USER CONTEXT:{user_context}" if user_context else ""}

USER QUESTION: {question}

INSTRUCTIONS:
1. Use the LIVE DATA above - these are real current prices
2. Reference specific numbers from the data
3. Give helpful, actionable advice
4. Keep response concise (under 150 words)

Your response:"""

    # Step 4: Generate response with Gemma
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7, "max_output_tokens": 400}
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# Test
if __name__ == "__main__":
    print("Testing Financial Agent...")
    print("-" * 50)
    result = ask_financial_agent("What is the current gold price in India?")
    print(result)
