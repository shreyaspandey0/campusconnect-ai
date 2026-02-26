import google.generativeai as genai

API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"

print("Testing gemini-2.5-compute-preview-10-2025...")
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-compute-preview-10-2025')
    
    response = model.generate_content("Hello")
    print(f"✅ SUCCESS!")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"❌ FAILED!")
    print(f"Full Error: {e}")
    print(f"Error Type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
