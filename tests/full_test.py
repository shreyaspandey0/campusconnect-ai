import google.generativeai as genai
import traceback

API_KEY = "AIzaSyC7VyIr97MU4hUtmfMvwmw3cJ7G6_OSH6c"

print("="*50)
print("COMPREHENSIVE API KEY TEST")
print("="*50)

# Test 1: List all available models
print("\n1. Listing all available models...")
try:
    genai.configure(api_key=API_KEY)
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"   ✓ {m.name}")
    
    if not available_models:
        print("   ❌ NO MODELS AVAILABLE!")
except Exception as e:
    print(f"   ❌ Error listing models: {e}")
    traceback.print_exc()

# Test 2: Try each model
print("\n2. Testing each available model...")
test_models = [
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-2.0-flash',
]

for model_name in test_models:
    print(f"\n   Testing: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi")
        print(f"   ✅ SUCCESS! Response: {response.text[:50]}...")
        break  # Found a working model
    except Exception as e:
        error_msg = str(e)
        if '429' in error_msg:
            print(f"   ❌ 429 Rate Limit")
        elif '404' in error_msg:
            print(f"   ❌ 404 Not Found")
        else:
            print(f"   ❌ Error: {error_msg[:100]}")

print("\n" + "="*50)
