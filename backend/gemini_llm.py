# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     raise RuntimeError("GEMINI_API_KEY not found in .env")

# genai.configure(api_key=api_key)

# # ✅ WORKING MODEL FOR YOUR KEY
# model = genai.GenerativeModel("models/gemini-2.0-flash")

# def gemini(prompt: str) -> str:
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"[Gemini Error] {str(e)}"




import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

# Configure API
genai.configure(api_key=api_key)

# ✅ GEMMA MODEL (NO BILLING REQUIRED)
model = genai.GenerativeModel("models/gemma-3-4b-it")

def gemini(prompt: str) -> str:
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
        return f"[Gemma Error] {str(e)}"

