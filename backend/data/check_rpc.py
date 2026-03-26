import os, sys
from supabase import create_client
from dotenv import load_dotenv; load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
sb = create_client(url, key)

print("Checking match_skill_nodes RPC...")

# 1. Test with new parameter 'filter_domain'
try:
    print("Testing with filter_domain='test'...")
    res = sb.rpc('match_skill_nodes', {
        'query_embedding': [0] * 1024,
        'match_threshold': 0.5,
        'match_count': 1,
        'filter_domain': 'test'
    }).execute()
    print("✅ Filter domain supported!")
except Exception as e:
    print(f"❌ Filter domain NOT supported: {e}")

# 2. Test without filter_domain
try:
    print("Testing old version (no filter)...")
    res = sb.rpc('match_skill_nodes', {
        'query_embedding': [0] * 1024,
        'match_threshold': 0.5,
        'match_count': 1
    }).execute()
    print("✅ Old version (no filter) is present!")
except Exception as e:
    print(f"❌ Old version NOT working: {e}")
