import google.generativeai as genai

API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"

print("Testing gemini-1.5-pro...")
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    response = model.generate_content("Say hello")
    print(f"✅ SUCCESS! Response: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED!")
    print(f"Error: {e}")
    print(f"Error Type: {type(e).__name__}")
    
print("\nListing ALL available models for this key:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  ✓ {m.name}")
except Exception as e2:
    print(f"Could not list models: {e2}")
