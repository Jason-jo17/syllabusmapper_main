import os, asyncio
from supabase import create_client
from dotenv import load_dotenv; load_dotenv()

async def debug_mappings():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    sb = create_client(url, key)
    
    # 1. Find the course
    course_name = "LICs Lab using PSPICE"
    print(f"--- Debugging Course: {course_name} ---")
    r = sb.table('courses').select('*').ilike('course_title', f'%{course_name}%').execute()
    if not r.data:
        print("Course NOT found in database.")
        return
        
    c = r.data[0]
    cid = c['id']
    code = c['course_code']
    print(f"ID: {cid}")
    print(f"Code: {code}")
    print(f"Syllabus ID: {c['syllabus_id']}")

    # 2. Check COs
    rcos = sb.table('course_outcomes').select('id, co_code').eq('course_id', cid).execute()
    print(f"COs found: {len(rcos.data)}")
    for co in rcos.data:
        print(f"  - {co['co_code']} (ID: {co['id']})")

    # 3. Check Mappings
    rmaps = sb.table('co_skill_mappings').select('*').eq('course_id', cid).execute()
    print(f"Skill Mappings found: {len(rmaps.data)}")
    
    # 4. Check if any mappings exist for this course_code but DIFFERENT course_id
    print("\n--- Checking for orphaned mappings (matching code but different ID) ---")
    # This is harder to query directly, but let's see if there are multiple versions of this course
    r_multi = sb.table('courses').select('id, syllabus_id').eq('course_code', code).execute()
    if len(r_multi.data) > 1:
        print(f"WARNING: Found {len(r_multi.data)} instances of course code {code}")
        for inst in r_multi.data:
            rm = sb.table('co_skill_mappings').select('id').eq('course_id', inst['id']).execute()
            print(f"  Course ID {inst['id']} has {len(rm.data)} mappings.")
    else:
        print("Only one instance of this course found.")

if __name__ == "__main__":
    asyncio.run(debug_mappings())
