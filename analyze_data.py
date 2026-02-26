def analyze_admission():
    with open('website_data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "admission" in line.lower():
             print(f"\n--- FOUND ADMISSION: {line.strip()} (Line {i+1}) ---")
             # Print next 10 lines
             for j in range(1, 11):
                 if i+j < len(lines):
                     print(f"{i+j+1}: {lines[i+j].strip()}")

analyze_admission()
