import os
import httpx
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# Supabase configuration
su = os.environ.get('SUPABASE_URL')
sk = os.environ.get('SUPABASE_KEY')

@router.get("")
async def get_all_events():
    if not su or not sk:
        return []
        
    h = {"apikey": sk, "Authorization": f"Bearer {sk}"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{su}/rest/v1/events?select=*", headers=h, timeout=10.0)
            if r.status_code == 200:
                events = r.json()
                # Ensure skills_addressed is parsed if it comes as a string (though it should be JSONB)
                for e in events:
                    if isinstance(e.get('skills_addressed'), str):
                        try:
                            import json
                            e['skills_addressed'] = json.loads(e['skills_addressed'])
                        except:
                            e['skills_addressed'] = []
                return events
            return []
    except Exception as e:
        print(f"Error fetching events from DB: {e}")
        return []

@router.get("/domain/{domain}")
async def get_events_by_domain(domain: str):
    all_events = await get_all_events()
    domain = domain.lower()
    return [
        e for e in all_events 
        if domain in str(e.get("knowledge_domain_1", "")).lower()
        or domain in str(e.get("knowledge_domain_2", "")).lower()
        or domain in str(e.get("knowledge_domain_3", "")).lower()
    ]

@router.get("/assessments")
async def get_assessments(skill: str = None):
    if not su or not sk:
        return []
        
    h = {"apikey": sk, "Authorization": f"Bearer {sk}"}
    try:
        async with httpx.AsyncClient() as client:
            # 1. Query skill_assessments table
            url = f"{su}/rest/v1/skill_assessments?select=*"
            if skill:
                # Search in both skill_knowledge and knowledge_set
                url += f"&or=(skill_knowledge.ilike.*{skill}*,knowledge_set.ilike.*{skill}*)"
            
            r = await client.get(url, headers=h, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                transformed = []
                for a in data:
                    # Map to frontend expectations
                    # s: skill, ks: knowledge set, d: description, bl: bloom level
                    res = {
                        "s": a.get("skill_knowledge"),
                        "ks": a.get("knowledge_set"),
                        "d": a.get("domain"),
                        "bl": 3, # Fallback bl
                        "bln": "Applying",
                        "mq": [m.get("question") for m in a.get("mcqs", [])],
                        "sq": [s.get("question") for s in a.get("subjective_tasks", [])],
                        "sh": [s.get("hint") for s in a.get("subjective_tasks", [])],
                        "rub": []
                    }
                    
                    # Transform Rubrics (3-point to 5-point mapping)
                    for s_task in a.get("subjective_tasks", []):
                        rubric_set = []
                        for r_item in s_task.get("rubrics", []):
                            rubric_set.append({
                                "el": r_item.get("element"),
                                "desc": r_item.get("description"),
                                "s5": r_item.get("score5_expert"),
                                "s4": "-",
                                "s3": r_item.get("score3_proficient"),
                                "s2": "-",
                                "s1": r_item.get("score1_emerging")
                            })
                        if rubric_set:
                            res["rub"].append(rubric_set)
                    
                    transformed.append(res)
                
                # If no DB results, fallback to file (temporary)
                if not transformed:
                    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    ASSESSMENTS_PATH = os.path.join(BASE_DIR, "data", "assessments.json")
                    if os.path.exists(ASSESSMENTS_PATH):
                        with open(ASSESSMENTS_PATH, 'r') as f:
                            import json
                            data = json.load(f)
                            if skill:
                                skill = skill.lower()
                                return [a for a in data if skill in str(a.get("s", "")).lower()]
                            return data
                return transformed
            return []
    except Exception as e:
        print(f"Error fetching assessments: {e}")
        return []

@router.get("/{event_id}")
async def get_event(event_id: str):
    if not su or not sk:
        return {"error": "DB config missing"}
        
    h = {"apikey": sk, "Authorization": f"Bearer {sk}"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{su}/rest/v1/events?id=eq.{event_id}&select=*", headers=h, timeout=10.0)
            if r.status_code == 200:
                data = r.json()
                if data:
                    event = data[0]
                    if isinstance(event.get('skills_addressed'), str):
                        import json
                        event['skills_addressed'] = json.loads(event['skills_addressed'])
                    return event
            return {"error": "Event not found"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/assignments/{event_id}")
async def get_assignment(event_id: str):
    # Assignments are still file-based for now (temporary storage)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSIGNMENTS_PATH = os.path.join(BASE_DIR, "data", "assignments.json")
    if not os.path.exists(ASSIGNMENTS_PATH) or os.path.getsize(ASSIGNMENTS_PATH) == 0:
        return {}
    with open(ASSIGNMENTS_PATH, 'r') as f:
        try:
            import json
            data = json.load(f)
            return data.get(event_id, {})
        except:
            return {}

@router.post("/assignments/{event_id}")
async def save_assignment(event_id: str, payload: Dict[str, Any]):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSIGNMENTS_PATH = os.path.join(BASE_DIR, "data", "assignments.json")
    data = {}
    if os.path.exists(ASSIGNMENTS_PATH) and os.path.getsize(ASSIGNMENTS_PATH) > 0:
        with open(ASSIGNMENTS_PATH, 'r') as f:
            try:
                import json
                data = json.load(f)
            except:
                data = {}
    data[event_id] = payload
    with open(ASSIGNMENTS_PATH, 'w') as f:
        import json
        json.dump(data, f)
    return {"status": "success"}
