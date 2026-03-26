import os, httpx
from typing import Optional
from fastapi import APIRouter
from dotenv import load_dotenv

router = APIRouter()

@router.get("")
async def get_syllabi():
    load_dotenv()
    su = os.environ.get('SUPABASE_URL', '')
    sk = os.environ.get('SUPABASE_KEY', '')
    if not su or not sk: return []
    
    h = {"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    try:
        r = httpx.get(url=f"{su}/rest/v1/syllabi?select=*", headers=h, timeout=10.0)
        if r.status_code == 200: return r.json()
    except Exception as e:
        print(f"Error fetching syllabi: {e}")
    return []

@router.get("/{id}/courses")
async def get_syllabus_courses(id: str):
    load_dotenv()
    su = os.environ.get('SUPABASE_URL', '')
    sk = os.environ.get('SUPABASE_KEY', '')
    if not su or not sk: return []
    
    h = {"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    try:
        # 1. Fetch courses
        print(f"Fetching courses for syllabus {id}...")
        r = httpx.get(url=f"{su}/rest/v1/courses?syllabus_id=eq.{id}&select=*", headers=h, timeout=15.0)
        if r.status_code != 200: 
            print(f"Courses fetch failed: {r.status_code}")
            return []
        courses = r.json()
        if not courses: 
            print("No courses found for syllabus.")
            return []
        
        # 2. Fetch CO counts globally (batch)
        cids = ",".join([f'"{c["id"]}"' for c in courses])
        print(f"Fetching CO counts for {len(courses)} courses...")
        r_cos = httpx.get(url=f"{su}/rest/v1/course_outcomes?course_id=in.({cids})&select=course_id", headers=h, timeout=15.0)
        cos = r_cos.json() if r_cos.status_code == 200 else []
        
        # 3. Fetch Mapping counts
        print("Fetching skill mappings...")
        r_maps = httpx.get(url=f"{su}/rest/v1/co_skill_mappings?syllabus_id=eq.{id}&select=course_id", headers=h, timeout=15.0)
        maps = r_maps.json() if r_maps.status_code == 200 else []
        
        from vtu_data import get_course_title
        for c in courses:
            code = c.get("course_code")
            db_title = c.get("title") or c.get("course_title")
            vtu_title = get_course_title(code) if code else None
            c["course_title"] = db_title or vtu_title or code or "Unnamed Course"
            c["co_count"] = len([x for x in cos if x.get('course_id') == c['id']])
            c["skill_count"] = len([x for x in maps if x.get('course_id') == c['id']])
            
        print("Successfully compiled course list.")
        return sorted(courses, key=lambda x: x.get("course_code", ""))
    except Exception as e:
        print(f"Error fetching syllabus courses: {e}")
        traceback.print_exc()
    return []
