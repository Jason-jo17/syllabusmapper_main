import pandas as pd
import math
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

CSV_PATH = r"D:\Event Mastersheet mockup - Copy of tester 2 (2).csv"

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
        return None
    return str(val)

@router.get("/")
async def get_all_events():
    try:
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

@router.get("/{event_id}")
async def get_event(event_id: str):
    all_events = await get_all_events()
    for e in all_events:
        if e.get("id") == event_id:
            return e
    return {"error": "Event not found"}

