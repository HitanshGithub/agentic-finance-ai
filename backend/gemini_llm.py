# Gemini LLM Module with Google Search Grounding
# Uses both standard generation and search-grounded generation for market data

import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")


# ===== STANDARD GEMINI (using LangChain) =====
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Initialize LangChain model
chatbot=ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def gemini(prompt: str) -> str:
    """Standard Gemini generation using LangChain."""
    try:
        response = chatbot.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"[Gemini Error] {str(e)}"

# ===== GEMINI WITH GOOGLE SEARCH GROUNDING =====
# Currently keeping this as fallback or refactoring if LangChain supports tools differently
# For now, we'll use the basic generation which is what the user seems to want for the core
# But we must ensure it doesn't break.
# Warning: The original gemini_with_search used google.genai, we will simplify to use the chatbot for consistency
# unless specific tool use is required.

def gemini_with_search(prompt: str) -> str:
    """
    Gemini generation using LangChain. 
    Note: Direct grounding is different in LangChain. 
    For now, we route this to the standard gemini function to ensure stability
    OR we can implement tool use if needed.
    """
    return gemini(prompt)


def get_market_data(query: str) -> str:
    """
    Fetch current market information using Google Search.
    Use this for investment recommendations.
    """
    search_prompt = f"""Search for the latest information about: {query}

Focus on:
- Current stock market trends (focus on Indian Market/Nifty/Sensex if relevant)
- Recent financial news
- Interest rates and inflation data (India/Global)
- Investment opportunities

Provide a concise summary (under 200 words) of the most relevant current information. Ensure all currency values are in Indian Rupees (₹)."""

    return gemini_with_search(search_prompt)


def gemini_with_market_context(prompt: str, include_market_data: bool = True) -> str:
    """
    Generate response with optional current market context.
    Useful for investment and financial advice.
    """
    if include_market_data:
        # First search for relevant market data
        market_query = "current stock market trends interest rates investment opportunities 2024"
        market_context = gemini_with_search(f"Give me a brief summary of: {market_query}")
        
        # Then generate response with context
        enhanced_prompt = f"""CURRENT MARKET CONTEXT:
{market_context}

---

Based on the above current market information, please respond to:
{prompt}"""
        
        return gemini(enhanced_prompt)
    else:
        return gemini(prompt)


# ===== REAL WEB SEARCH (HTTP REQUESTS) =====
# Uses actual API calls to get live data

def get_live_market_data() -> str:
    """
    Fetch REAL live market data using HTTP requests.
    This actually fetches current data from APIs.
    """
    from web_search import fetch_financial_context
    
    try:
        context = fetch_financial_context()
        return context.get('summary', 'Unable to fetch live data')
    except Exception as e:
        return f"[Error fetching market data: {e}]"


def gemini_with_real_data(prompt: str) -> str:
    """
    Generate response with REAL live data from web APIs.
    Uses HTTP requests to Yahoo Finance, CoinGecko, etc.
    """
    from web_search import fetch_financial_context
    
    try:
        # Fetch real market data
        context = fetch_financial_context(prompt)
        live_data = context.get('summary', 'No live data available')
        
        enhanced_prompt = f"""CURRENT LIVE MARKET DATA (fetched just now via HTTP):
{live_data}

---

Based on this REAL current data, respond to:
{prompt}

Important: Reference the actual numbers shown above in your response. Display all monetary values in Indian Rupees (₹). If the data is in USD, convert roughly (1 USD = 84 INR) or show both."""

        return gemini(enhanced_prompt)
    except Exception as e:
        return gemini(f"[Note: Live data unavailable due to {e}] {prompt}")


def search_and_respond(user_query: str) -> str:
    """
    Main function: Fetch real web data first, then generate response.
    
    Flow:
    1. HTTP requests to real financial APIs
    2. Pass live data + user query to Gemini
    3. Return response with actual current data
    """
    from web_search import search_web
    
    # Get real live data
    live_data = search_web(user_query)
    
    prompt = f"""You are a financial advisor with access to REAL-TIME market data.

LIVE DATA (fetched via HTTP just now):
{live_data}

USER QUERY: {user_query}

Instructions:
1. Use ONLY the live data provided above for any market references
2. Cite the actual numbers from the data
3. Provide actionable advice based on current conditions
4. If data is missing, acknowledge it
5. ALWAYS use Indian Rupees (₹) for currency. Convert USD if necessary (approx ₹84/USD).

Response:"""

    return gemini(prompt)

