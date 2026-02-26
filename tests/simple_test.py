import google.generativeai as genai

print("FINAL SIMPLE TEST")
print("-" * 40)

API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"
genai.configure(api_key=API_KEY)

# Try the simplest model
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content("Hi", generation_config={'max_output_tokens': 10})
    print(f"✅ IT WORKS! Response: {response.text}")
except Exception as e:
    print(f"❌ Failed: {str(e)[:200]}")
