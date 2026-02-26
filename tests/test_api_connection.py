import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("MODEL_NAME")

print(f"Testing API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")
print(f"Model: {model_name}")

if not api_key:
    print("API Key is missing!")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

try:
    response = model.generate_content("Hello, this is a test. Reply with 'API is working'.")
    print("Response received:")
    print(response.text)
except Exception as e:
    print(f"API Error: {e}")
