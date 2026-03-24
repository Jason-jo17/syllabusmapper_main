import os
import json
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "assignments.json")

def load_assignments():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_assignments(data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@router.get("/{event_id}")
async def get_assignment(event_id: str):
    data = load_assignments()
    return data.get(event_id, {})

@router.post("/{event_id}")
async def save_assignment(event_id: str, payload: Dict[str, Any]):
    data = load_assignments()
    data[event_id] = payload
    save_assignments(data)
    return {"status": "success", "event_id": event_id, "data": payload}
