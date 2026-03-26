import os, sys
from supabase import create_client
from dotenv import load_dotenv; load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
sb = create_client(url, key)

print("--- Supabase Integrity Check ---")

# Check match_skill_nodes
try:
    res = sb.rpc('match_skill_nodes', {
        'query_embedding': [0] * 1024,
        'match_threshold': 0.5,
        'match_count': 1,
        'filter_domain': 'test'
    }).execute()
    print("✅ RPC: 'match_skill_nodes' is UP-TO-DATE (supports filter_domain).")
except Exception as e:
    print(f"❌ RPC: 'match_skill_nodes' is OUTDATED (no filter_domain).")

# Check skill_assessments table
try:
    res = sb.table('skill_assessments').select('id').limit(1).execute()
    print("✅ Table: 'skill_assessments' EXISTS.")
except Exception as e:
    print(f"❌ Table: 'skill_assessments' MISSING.")

# Check events table RLS
try:
    res = sb.table('events').select('id').limit(1).execute()
    print("✅ Table: 'events' accessible (Select worked).")
except Exception as e:
    print(f"❌ Table: 'events' access issue (likely RLS).")
