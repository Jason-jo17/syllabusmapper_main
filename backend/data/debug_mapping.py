import os, sys
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv; load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
sb = create_client(url, key)

print("--- Comparing CSV vs Database ---")

# 1. Load CSV example
df = pd.read_csv('D:/Downloads2/skill_assessment_questions_complete.csv')
csv_sample = df[df['domain'] == 'Embedded systems'].iloc[0]
print(f"CSV Sample:")
print(f"  Domain: '{csv_sample['domain']}'")
print(f"  Skill:  '{csv_sample['skill_knowledge']}'")

# 2. Search Database for similar
print("\nSearching Database...")
nodes = sb.table('skill_nodes').select('domain, skill_description').eq('domain', 'Embedded systems').execute().data
print(f"Total Embedded nodes found: {len(nodes)}")

if nodes:
    print("DB Samples (First 5):")
    for n in nodes[:5]:
        print(f"  - '{n['skill_description']}'")
    
    # Check for direct match
    sk_csv = str(csv_sample['skill_knowledge']).lower().strip()
    matches = [n for n in nodes if str(n['skill_description']).lower().strip() == sk_csv]
    print(f"\nDirect matches for '{sk_csv}': {len(matches)}")

    if not matches:
        print("\nNo direct match. Checking for sub-string match...")
        sub_matches = [n for n in nodes if sk_csv in str(n['skill_description']).lower()]
        print(f"Sub-string matches: {len(sub_matches)}")
        if sub_matches:
            for sm in sub_matches[:3]:
                print(f"  - '{sm['skill_description']}'")
