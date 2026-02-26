import google.generativeai as genai

API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"

print("Testing gemini-1.5-flash...")
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content("Say hello in one word")
    print(f"✅ SUCCESS! Response: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED!")
    print(f"Error: {e}")
    print(f"Error Type: {type(e).__name__}")
