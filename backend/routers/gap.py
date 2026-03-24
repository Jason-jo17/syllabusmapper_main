import os, httpx
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from services.gap_analyser import analyse

router = APIRouter()

class GapRequest(BaseModel):
    syllabus_id: str
    job_role_id: str
def get_headers():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '')
    return url, {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

@router.post("/analyse")
async def analyse_gaps_endpoint(req: GapRequest):
    return await analyse(req.syllabus_id, req.job_role_id)

@router.get("/{syllabus_id}/{role_id}")
async def get_gap(syllabus_id: str, role_id: str):
    url, h = get_headers()
    if not url: return {}
    try:
        r = httpx.get(f"{url}/rest/v1/gap_reports?syllabus_id=eq.{syllabus_id}&job_role_id=eq.{role_id}&select=*", headers=h, timeout=10.0)
        if r.status_code == 200:
            data = r.json()
            return data[0] if data else {}
    except Exception as e:
        print(f"Error fetching gap report: {e}")
    return {}
