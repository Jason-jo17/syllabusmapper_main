import os
import httpx
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# Supabase configuration
su = os.environ.get('SUPABASE_URL')
sk = os.environ.get('SUPABASE_KEY')

@router.get("/")
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
    # Assessments might still be in a JSON file if not yet migrated to DB
    # We can keep the file logic for now as a fallback
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ASSESSMENTS_PATH = os.path.join(BASE_DIR, "data", "assessments.json")
    if not os.path.exists(ASSESSMENTS_PATH):
        return []
    with open(ASSESSMENTS_PATH, 'r') as f:
        try:
            import json
            data = json.load(f)
            if skill:
                skill = skill.lower()
                return [a for a in data if skill in a.get("s", "").lower()]
            return data
        except:
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
