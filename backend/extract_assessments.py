import json
import re

html_path = r"D:\Downloads2\skill_assessment_portal_v6_events.html"
output_path = r"d:\Downloads2\syllabusmapper\backend\data\assessments.json"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# The DB array is stored as `const DB=[{...}];`
match = re.search(r"const DB=(\[.*?\]);", content, re.DOTALL)
if match:
    db_json_str = match.group(1)
    
    # Let's save it directly to the json file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(db_json_str)
    
    # Try parsing it to ensure it's valid JSON
    try:
        parsed = json.loads(db_json_str)
        print(f"Successfully extracted and saved {len(parsed)} assessment records to {output_path}")
    except json.JSONDecodeError as e:
        print(f"Extraction successful but validation failed: {e}")
else:
    print("Could not find the DB array in the HTML file.")
