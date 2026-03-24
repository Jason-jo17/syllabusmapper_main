import os
import json
from supabase import create_client
from dotenv import load_dotenv

def check_db():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    if not url or not key:
        print("MISSING ENV")
        return
    
    sb = create_client(url, key)
    
    # Try a simple select * on skill_nodes
    try:
        res = sb.table('skill_nodes').select('*').limit(1).execute()
        if res.data:
            print("Skill Node Columns:", res.data[0].keys())
        else:
            print("No skill nodes found")
    except Exception as e:
        print(f"Error skill_nodes: {e}")

    # Try a simple select * on courses
    try:
        res = sb.table('courses').select('*').limit(1).execute()
        if res.data:
            print("Course Columns:", res.data[0].keys())
        else:
            print("No courses found")
    except Exception as e:
        print(f"Error courses: {e}")

if __name__ == "__main__":
    check_db()
