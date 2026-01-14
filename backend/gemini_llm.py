# Gemini LLM Module with Google Search Grounding
# Uses both standard generation and search-grounded generation for market data

import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")


# ===== STANDARD GEMINI (using google.generativeai) =====
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemma-3-27b-it")


def gemini(prompt: str) -> str:
    """Standard Gemini generation without search."""
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 300
            }
        )
        return response.text
    except Exception as e:
        return f"[Gemini Error] {str(e)}"


# ===== GEMINI WITH GOOGLE SEARCH GROUNDING =====
# Uses the newer google.genai client for search capabilities

def gemini_with_search(prompt: str) -> str:
    """
    Gemini generation with Google Search grounding.
    Uses real-time web search to get current market data.
    """
    try:
        from google import genai
        from google.genai import types
        
        # Create client with API key
        client = genai.Client(api_key=api_key)
        
        # Enable Google Search tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            temperature=0.7,
            max_output_tokens=500
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        
        return response.text
        
    except ImportError:
        # Fallback if google.genai not available
        return gemini(f"[Note: Search unavailable, using cached knowledge] {prompt}")
    except Exception as e:
        # Fallback to standard gemini on any error
        print(f"Search grounding error: {e}, falling back to standard")
        return gemini(prompt)


def get_market_data(query: str) -> str:
    """
    Fetch current market information using Google Search.
    Use this for investment recommendations.
    """
    search_prompt = f"""Search for the latest information about: {query}

Focus on:
- Current stock market trends
- Recent financial news
- Interest rates and inflation data
- Investment opportunities

Provide a concise summary (under 200 words) of the most relevant current information."""

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
