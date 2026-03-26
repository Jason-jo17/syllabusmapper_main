import pandas as pd
import asyncio, os, json, uuid, sys, math
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client, ClientOptions

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')
options = ClientOptions(postgrest_client_timeout=60)
sb = create_client(url, key, options=options)

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)): return None
    return str(val).strip()

async def seed_events(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        return

    print("Clearing existing events...")
    sb.table('events').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

    print(f"Reading Master CSV with skip-headers: {csv_path}...")
    # Skip first 5 rows of meta-headers
    df = pd.read_csv(csv_path, skiprows=5, header=None)
    
    events_agg = {} # key: event_name

    for i, row in df.iterrows():
        try:
            domain_col = sanitize_value(row.iloc[1])
            event_name = sanitize_value(row.iloc[2])
            if not event_name: continue
            
            ks = sanitize_value(row.iloc[6])
            sk = sanitize_value(row.iloc[7])
            bl = sanitize_value(row.iloc[8])

            if event_name not in events_agg:
                events_agg[event_name] = {
                    "id": str(uuid.uuid4()),
                    "event_name": event_name,
                    "organizing_body": sanitize_value(row.iloc[3]),
                    "description": sanitize_value(row.iloc[4]),
                    "problem_statement": sanitize_value(row.iloc[5]),
                    "registration_links": None, "keywords": None, "event_registration_deadline": None, "event_date": None, "location": None, "mode": None,
                    "knowledge_domain_1": domain_col,
                    "event_type": "Hackathon", # Default based on context
                    "skills_addressed": []
                }
            
            if ks or sk:
                events_agg[event_name]["skills_addressed"].append({
                    "knowledge_set": ks,
                    "skill_knowledge": sk,
                    "bl_level": bl
                })
        except Exception as e:
            print(f"  [-] Error at row {i+1}: {e}")

    inserts = list(events_agg.values())
    print(f"Inserting {len(inserts)} unique aggregated events...")
    for i in range(0, len(inserts), 50):
        sb.table('events').insert(inserts[i:i+50]).execute()
        print(f"  [+] Inserted chunk {i//50 + 1}")

    print("Event Seeding Finalized.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else 'backend/data/Event Mastersheet mockup - Domain, skillset L C (9).csv'
    asyncio.run(seed_events(path))
