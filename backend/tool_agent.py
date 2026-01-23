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
# Configure Gemini with LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)


# ===== DATA FETCHING TOOLS =====

def get_current_date() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_gold_price_india() -> str:
    """Fetch current gold prices in India from GoodReturns."""
    try:
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Fetching from the standard gold-rates.html page (User referred to as gold-price.html)
        response = requests.get("https://www.goodreturns.in/gold-rates.html", headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple text scraping strategy for GoodReturns specific structure
            # Looking for 24K Gold price
            # Text often appears as "24K Gold Price Today ... ₹ 1,59,710"
            text = soup.get_text()
            
            # Regex to find 24K price, looking for standard format
            import re
            # Matches "24K Gold" followed by price
            # Adjust regex to capture the price which might include newlines or spaces
            # Example target: "24K Gold... 1,59,710"
            
            # Try finding specific price container if possible, otherwise regex on full text
            # Goodreturns usually has tables. Let's look for "24K" in text.
            
            # fallback to specific patterns based on user screenshot prices (~1.5L)
            matches = re.findall(r'24K\s+Gold.*?(?:Rs\.?|₹)\s*([\d,]+)', text, re.IGNORECASE | re.DOTALL)
            
            if matches:
                 # Taking the first match which is usually 10g
                price_str = matches[0].strip()
                return f"Gold 24K: ₹{price_str}/10g (Source: GoodReturns)"
            
            # Alternative: direct search for price pattern if label is separate
            all_prices = re.findall(r'(?:Rs\.?|₹)\s*([\d,]{4,10})', text)
            for p in all_prices:
                p_val = int(p.replace(',', ''))
                if 140000 <= p_val <= 200000: # Contextual validation for 10g Gold
                     return f"Gold 24K: ₹{p}/10g (Source: GoodReturns)"

    except Exception as e:
        print(f"Gold scraping error: {e}")
    
    return "Gold price unavailable (Check goodreturns.in)"


def get_stock_market_data() -> str:
    """Fetch NIFTY and SENSEX from GoodReturns."""
    try:
        from bs4 import BeautifulSoup
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get("https://www.goodreturns.in/", headers=headers, timeout=15)
        
        results = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            import re
            
            # Regex for Sensex
            # Matches "Sensex" followed closely by number like "82,308.85"
            sensex_match = re.search(r'Sensex\s*[:\-]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
            if sensex_match:
                results.append(f"SENSEX: {sensex_match.group(1)}")
            
            # Regex for Nifty
            nifty_match = re.search(r'Nifty\s*[:\-]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
            if nifty_match:
                results.append(f"NIFTY 50: {nifty_match.group(1)}")
                
        if results:
            return f"Indian Markets: " + " | ".join(results) + " (Source: GoodReturns)"
            
    except Exception as e:
        print(f"Stock scraping error: {e}")
        
    return "Indian Market data unavailable (Check goodreturns.in)"


def get_silver_price() -> str:
    """Fetch current silver prices from GoodReturns."""
    try:
        from bs4 import BeautifulSoup
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # Fetching from the standard silver-rates.html page (User referred to as silver-price.html)
        response = requests.get("https://www.goodreturns.in/silver-rates.html", headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            import re
            
            # Looking for 1kg price, which user says is around 3,30,000+
            # Regex to find "Silver" followed by price
            # Pattern: "Silver... ₹ 3,40,000"
            
            # Look for large numbers associated with Silver
            matches = re.findall(r'(?:Rs\.?|₹)\s*([\d,]+)', text)
            for match in matches:
                price = int(match.replace(',', ''))
                # Validation range based on user input (3.3L to 4.0L)
                if 300000 <= price <= 400000:
                    return f"Silver: ₹{price:,}/kg (Source: GoodReturns)"
                    
    except Exception as e:
        print(f"Silver scraping error: {e}")
    
    return "Silver price unavailable (Check goodreturns.in)"


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
            goals = ", ".join([f"{g.get('name', 'Goal')} (Target: ₹{g.get('target', 0)})" for g in context['goals']])
            user_context += f"\n- Goals: {goals}"
    
    # Step 3: Create prompt with live data
    prompt = f"""You are a helpful financial advisor.

{live_data}

OPTIONAL BACKGROUND INFO (only use if specific to the question):
{user_context if user_context else "None provided"}

USER QUESTION: {question}

**STRICT INSTRUCTIONS**:
1. **Analyze Intent**:
   - **Greeting/Small Talk**: Respond naturally. Do NOT mention crypto, stocks, or goals.
   - **General Market Question** (e.g., "best sectors", "gold price", "market trends"): Answer using ONLY the LIVE DATA. **ABSOLUTELY DO NOT** mention the user's specific goals (like "wedding", "car", etc.) unless the user *explicitly* names them in the *current* question. Treat general questions as general.
   - **Personal Advice**: If the user asks "how do *I* save" or "for *my* goal", THEN use the Background Info.

2. **Content Rules**:
   - Reference specific numbers from LIVE DATA.
   - ALWAYS use Indian Rupees (₹).
   - If answering a general question, do NOT say "Considering your wedding fund...". Just answer the question.

3. Keep response concise (under 150 words).

Your response:"""

    # Step 4: Generate response with Gemma
    try:
        response = model.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"


# Test
if __name__ == "__main__":
    print("Testing Financial Agent...")
    print("-" * 50)
    result = ask_financial_agent("What is the current gold price in India?")
    print(result)
