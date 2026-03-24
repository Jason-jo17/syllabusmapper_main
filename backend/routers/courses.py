import os, httpx
from typing import Optional
from fastapi import APIRouter
from dotenv import load_dotenv

router = APIRouter()

@router.get("/")
async def get_all_courses():
    load_dotenv()
    su = os.environ.get('SUPABASE_URL', '')
    sk = os.environ.get('SUPABASE_KEY', '')
    if not su or not sk: return []
    
    h = {"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    try:
        r = httpx.get(url=f"{su}/rest/v1/courses?select=*", headers=h, timeout=10.0)
        if r.status_code == 200:
            from vtu_data import get_course_title
            data = r.json()
            for c in data:
                code = c.get("course_code")
                db_title = c.get("title") or c.get("course_title")
                vtu_title = get_course_title(code) if code else None
                c["course_title"] = db_title or vtu_title or code or "Unnamed Course"
            return data
    except Exception as e:
        print(f"Error fetching all courses: {e}")
    return []

@router.get("/{id}/cos/")
async def get_course_cos(id: str):
    load_dotenv()
    su = os.environ.get('SUPABASE_URL', '')
    sk = os.environ.get('SUPABASE_KEY', '')
    if not su or not sk: return []
    
    h = {"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    try:
        r = httpx.get(url=f"{su}/rest/v1/course_outcomes?course_id=eq.{id}&select=*", headers=h, timeout=10.0)
        if r.status_code == 200:
            data = r.json()
            seen = set()
            unique = []
            for x in data:
                code = x.get("co_code")
                if code and code not in seen:
                    seen.add(code)
                    unique.append(x)
            return sorted(unique, key=lambda x: x.get("co_code", ""))
    except Exception as e:
        print(f"Error fetching COs: {e}")
    return []

@router.get("/{id}/skills/")
async def get_course_skills(id: str):
    load_dotenv()
    su = os.environ.get('SUPABASE_URL', '')
    sk = os.environ.get('SUPABASE_KEY', '')
    if not su or not sk: return []
    
    h = {"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json"}
    try:
        # Join with skill_nodes
        r = httpx.get(url=f"{su}/rest/v1/co_skill_mappings?course_id=eq.{id}&select=*,skill_nodes(*)", headers=h, timeout=10.0)
        if r.status_code == 200:
            data = r.json()
            skills = []
            seen = set()
            for m in data:
                sn = m.get('skill_nodes')
                if sn and sn.get('id') and sn['id'] not in seen:
                    seen.add(sn['id'])
                    skills.append(sn)
            return skills
    except Exception as e:
        print(f"Error fetching skills: {e}")
    return []
