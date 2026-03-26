import pandas as pd
import asyncio, os, json, uuid, sys, math
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')
sb = create_client(url, key)

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
        return None
    return str(val).strip()

async def seed_events(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        return

    print(f"Reading CSV: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Clear existing events to prevent duplicates
    print("Clearing existing events...")
    sb.table('events').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

    inserts = []
    for i, row in df.iterrows():
        try:
            event_name = sanitize_value(row.iloc[0])
            if not event_name or event_name == "":
                continue
                
            skills_addressed = []
            # Map skills/knowledge sets (same as in router)
            for k_col, s_col, bl_col in [(32, 33, 34), (35, 36, 37), (38, 39, 40)]:
                if k_col < len(row) and s_col < len(row):
                    ks = sanitize_value(row.iloc[k_col])
                    sk = sanitize_value(row.iloc[s_col])
                    bl = sanitize_value(row.iloc[bl_col])
                    if ks or sk:
                        skills_addressed.append({
                            "knowledge_set": ks,
                            "skill_knowledge": sk,
                            "bl_level": bl
                        })
            
            event = {
                "id": str(uuid.uuid4()),
                "event_name": event_name,
                "organizing_body": sanitize_value(row.iloc[1]) if 1 < len(row) else None,
                "description": sanitize_value(row.iloc[2]) if 2 < len(row) else None,
                "problem_statement": sanitize_value(row.iloc[3]) if 3 < len(row) else None,
                "registration_links": sanitize_value(row.iloc[4]) if 4 < len(row) else None,
                "keywords": sanitize_value(row.iloc[5]) if 5 < len(row) else None,
                "event_registration_deadline": sanitize_value(row.iloc[6]) if 6 < len(row) else None,
                "event_date": sanitize_value(row.iloc[7]) if 7 < len(row) else None,
                "location": sanitize_value(row.iloc[8]) if 8 < len(row) else None,
                "mode": sanitize_value(row.iloc[9]) if 9 < len(row) else None,
                "knowledge_domain_1": sanitize_value(row.iloc[15]) if 15 < len(row) else None,
                "knowledge_domain_2": sanitize_value(row.iloc[16]) if 16 < len(row) else None,
                "knowledge_domain_3": sanitize_value(row.iloc[17]) if 17 < len(row) else None,
                "event_type": sanitize_value(row.iloc[30]) if 30 < len(row) else None,
                "emi_score": sanitize_value(row.iloc[31]) if 31 < len(row) else None,
                "skills_addressed": skills_addressed
            }
            inserts.append(event)
        except Exception as e:
            print(f"Error processing row {i}: {e}")

    print(f"Inserting {len(inserts)} events into Supabase...")
    for i in range(0, len(inserts), 100):
        sb.table('events').insert(inserts[i:i+100]).execute()
        print(f"Inserted chunk {i//100 + 1}")

    print("Event Seeding Completed Successfully!")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'backend/data/Event Mastersheet mockup - Domain, skillset L C (9).csv'
    asyncio.run(seed_events(path))
