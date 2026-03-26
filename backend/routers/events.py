import os
import pandas as pd
import math
import json
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

# Locate the CSV relative to this file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Try multiple possible locations for the data folder
DATA_DIRS = [
    os.path.join(BASE_DIR, "data"),
    os.path.join(os.path.dirname(BASE_DIR), "data"), # Project root/data
    "/app/backend/data", # Railway specific
    "/app/data"          # Railway specific
]

def find_file(filename):
    for d in DATA_DIRS:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None

CSV_FILENAME = "Event Mastersheet mockup - Domain, skillset L C (9).csv"
ASSESSMENTS_FILENAME = "assessments.json"
ASSIGNMENTS_FILENAME = "assignments.json"

CSV_PATH = find_file(CSV_FILENAME)
ASSESSMENTS_PATH = find_file(ASSESSMENTS_FILENAME)
ASSIGNMENTS_PATH = find_file(ASSIGNMENTS_FILENAME)

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
        return None
    return str(val)

@router.get("/")
async def get_all_events():
    try:
        if not CSV_PATH:
            print(f"Events CSV not found in any of: {DATA_DIRS}")
            return []
            
        df = pd.read_csv(CSV_PATH)
        events = []
        for i, row in df.iterrows():
            event_name = sanitize_value(row.iloc[0])
            if not event_name or event_name.strip() == "":
                continue
                
            event = {
                "id": f"event_{i}",
                "event_name": event_name,
                "organizing_body": sanitize_value(row.iloc[1]),
                "description": sanitize_value(row.iloc[2]),
                "problem_statement": sanitize_value(row.iloc[3]),
                "registration_links": sanitize_value(row.iloc[4]),
                "keywords": sanitize_value(row.iloc[5]),
                "event_registration_deadline": sanitize_value(row.iloc[6]),
                "event_date": sanitize_value(row.iloc[7]),
                "location": sanitize_value(row.iloc[8]),
                "mode": sanitize_value(row.iloc[9]),
                "knowledge_domain_1": sanitize_value(row.iloc[15]),
                "knowledge_domain_2": sanitize_value(row.iloc[16]),
                "knowledge_domain_3": sanitize_value(row.iloc[17]),
                "event_type": sanitize_value(row.iloc[30]),
                "emi_score": sanitize_value(row.iloc[31]),
                "skills_addressed": []
            }
            
            # Map skills/knowledge sets
            for k_col, s_col, bl_col in [(32, 33, 34), (35, 36, 37), (38, 39, 40)]:
                ks = sanitize_value(row.iloc[k_col])
                sk = sanitize_value(row.iloc[s_col])
                bl = sanitize_value(row.iloc[bl_col])
                if ks or sk:
                    event["skills_addressed"].append({
                        "knowledge_set": ks,
                        "skill_knowledge": sk,
                        "bl_level": bl
                    })
            
            events.append(event)
            
        return events
    except Exception as e:
        print(f"Error reading events CSV: {e}")
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
    if not ASSESSMENTS_PATH:
        print("Assessments JSON not found")
        return []
    with open(ASSESSMENTS_PATH, 'r') as f:
        try:
            data = json.load(f)
        except:
            return []
        if skill:
            skill = skill.lower()
            return [a for a in data if skill in a.get("s", "").lower()]
        return data

@router.get("/{event_id}")
async def get_event(event_id: str):
    all_events = await get_all_events()
    for e in all_events:
        if e.get("id") == event_id:
            return e
    return {"error": "Event not found"}

@router.get("/assignments/{event_id}")
async def get_assignment(event_id: str):
    if not ASSIGNMENTS_PATH or not os.path.exists(ASSIGNMENTS_PATH):
        return {}
    if os.path.getsize(ASSIGNMENTS_PATH) == 0:
        return {}
        
    with open(ASSIGNMENTS_PATH, 'r') as f:
        try:
            data = json.load(f)
            return data.get(event_id, {})
        except:
            return {}

@router.post("/assignments/{event_id}")
async def save_assignment(event_id: str, payload: Dict[str, Any]):
    data = {}
    if os.path.exists(ASSIGNMENTS_PATH) and os.path.getsize(ASSIGNMENTS_PATH) > 0:
        with open(ASSIGNMENTS_PATH, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = {}
    
    data[event_id] = payload
    with open(ASSIGNMENTS_PATH, 'w') as f:
        json.dump(data, f)
    return {"status": "success"}
