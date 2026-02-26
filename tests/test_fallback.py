import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import search_local_data, load_system_instruction

print("Loading data...")
# Ensuring usage of actual files
# Note: app.py expects files in current directory or we need to change CWD
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Testing search_local_data fallback...")

queries = [
    "Hello",
    "Admissions",
    "djksfhkjsdhf", # Gibberish
    "" # Empty
]

for q in queries:
    res = search_local_data(q)
    print(f"Query: '{q}' => Response length: {len(res) if res else 0}")
    if not res:
        print("FAILED: Response was empty/None!")
    else:
        print("OK.")
