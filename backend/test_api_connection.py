from gemini_llm import gemini
import sys

print("Testing Gemini API connection...")
try:
    response = gemini("Hello! Just checking if you are working. Reply with 'Yes, I am working!' if you can hear me.")
    print("\nResponse from Gemini:")
    print("-" * 20)
    print(response)
    print("-" * 20)
    
    if "Gemini Error" in response:
        print("\n❌ API Error detected.")
        sys.exit(1)
    else:
        print("\n✅ API seems to be working correctly.")
        
except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    sys.exit(1)
