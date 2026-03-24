import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv('.env')

def debug():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    if not url or not key:
        print("MISSING ENV")
        return
    
    sb = create_client(url, key)
    cid = 'vtu_ece_reg_2024_21CS44'
    data = {
        'id': cid,
        'syllabus_id': 'vtu_ece_reg_2024',
        'course_code': '21CS44',
        'title': 'DEBUG TEST',
        'semester': 1,
        'credits': 4
    }
    
    print(f"Checking if {cid} exists...")
    check = sb.table('courses').select('id').eq('id', cid).execute()
    print(f"Exists: {check.data}")
    
    print(f"Trying upsert for {cid}...")
    try:
        res = sb.table('courses').upsert(data, on_conflict='id').execute()
        print(f"Upsert Success: {res.data}")
    except Exception as e:
        print(f"Upsert FAILED: {e}")
        
    print(f"Trying delete and insert for {cid}...")
    try:
        sb.table('courses').delete().eq('id', cid).execute()
        res = sb.table('courses').insert(data).execute()
        print(f"Delete+Insert Success: {res.data}")
    except Exception as e:
        print(f"Delete+Insert FAILED: {e}")

if __name__ == "__main__":
    debug()
