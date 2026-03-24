import os, httpx
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CollegeCreate(BaseModel):
    name: str
    short_code: str
    location: str = ""
    affiliation: str = ""

def get_headers():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '')
    if not url or not key: return None, None, {}
    return url, key, {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

@router.get("/")
async def get_colleges():
    url, key, h = get_headers()
    if not url: return []
    try:
        r = httpx.get(f"{url}/rest/v1/colleges?select=*", headers=h, timeout=10.0)
        if r.status_code == 200: return r.json()
    except Exception as e:
        print(f"Error fetching colleges: {e}")
    return []

@router.post("/")
async def create_college(college: CollegeCreate):
    url, key, h = get_headers()
    if not url: return {"error": "Config missing"}
    try:
        r = httpx.post(f"{url}/rest/v1/colleges", headers=h, json=college.dict(), timeout=10.0)
        if r.status_code in [200, 201]: return r.json()
        return {"error": r.text}
    except Exception as e:
        return {"error": str(e)}

@router.get("/{id}/syllabi")
async def get_college_syllabi(id: str):
    url, key, h = get_headers()
    if not url: return []
    try:
        r = httpx.get(f"{url}/rest/v1/syllabi?college_id=eq.{id}&select=*", headers=h, timeout=10.0)
        if r.status_code == 200: return r.json()
    except Exception as e:
        print(f"Error fetching college syllabi: {e}")
    return []
