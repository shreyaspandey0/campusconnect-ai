import google.generativeai as genai

# Test the API key directly
API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"

print("Testing API Key...")
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    response = model.generate_content("Say hello")
    print(f"✅ SUCCESS! API Key is VALID")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED! Error: {e}")
    print(f"Error type: {type(e).__name__}")
