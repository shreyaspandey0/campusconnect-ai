
import app
import sys

# Mocking the app context if needed, or just testing the function
print("Testing search_local_data...")
query = "fees"
result = app.search_local_data(query)

if result:
    print("SUCCESS: Found result locally:")
    print(result)
else:
    print("FAILURE: No result found locally.")

print("-" * 20)
print("Testing with 'hostel'")
result = app.search_local_data("hostel")
if result:
    print("SUCCESS: Found result locally:")
    print(result)
else:
    print("FAILURE: No result found locally.")
