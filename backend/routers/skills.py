import os, httpx
from typing import Optional
from fastapi import APIRouter
from dotenv import load_dotenv

router = APIRouter()

@router.get("/")
async def get_skills(role: Optional[str] = None):
    load_dotenv()
    su = os.environ.get('SUPABASE_URL')
    sk = os.environ.get('SUPABASE_KEY')
    if not su or not sk:
        return []
        
    h = {"apikey": sk, "Authorization": f"Bearer {sk}"}
    
    # Use direct REST API
    select_cols = "id, job_role_id, level, domain, category, knowledge_set, concept, skill_description, bloom_level, tools, common_tag, co_primary_text, co_primary_course, co_primary_year, co_primary_sem"
    params = {"select": select_cols}
    
    if role and role != "undefined":
        # 1. Get role ID via ilike for robustness
        role_url = f"{su}/rest/v1/job_roles?role_name=ilike.*{role}*&select=id"
        r = httpx.get(url=role_url, headers=h)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                role_id = data[0]["id"]
                params["job_role_id"] = f"eq.{role_id}"
            else:
                 # Default to the primary ECE role if no match found to prevent massive fetch
                 ece_url = f"{su}/rest/v1/job_roles?role_name=ilike.*Embedded*&select=id"
                 r_ece = httpx.get(url=ece_url, headers=h)
                 if r_ece.status_code == 200:
                     ece_data = r_ece.json()
                     if isinstance(ece_data, list) and len(ece_data) > 0:
                        params["job_role_id"] = f"eq.{ece_data[0]['id']}"

    nodes_url = f"{su}/rest/v1/skill_nodes"
    r = httpx.get(url=nodes_url, headers=h, params=params)
    if r.status_code == 200:
        return r.json()
    return []
