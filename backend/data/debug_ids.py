import os, sys
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv; load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
sb = create_client(url, key)

syl_id = "ece00000-0000-0000-0000-000000000000"

print("--- Checking ID Consistency ---")

# 1. Get all courses in DB for this syllabus
res = sb.table('courses').select('id, course_code').eq('syllabus_id', syl_id).execute()
db_courses = {c['id']: c['course_code'] for c in res.data}
print(f"Courses in DB: {len(db_courses)}")

# 2. Check a few IDs
if db_courses:
    first_id = list(db_courses.keys())[0]
    print(f"Sample DB ID: {first_id} -> {db_courses[first_id]}")

# 3. Check for specific problematic ID from logs
prob_id = "547781d9-b756-8d05c6e61cff" # from Step 1814
if prob_id in db_courses:
    print(f"✅ Problematic ID {prob_id} IS in DB!")
else:
    print(f"❌ Problematic ID {prob_id} NOT in DB!")
