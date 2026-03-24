import os
import json
from fastapi import APIRouter

router = APIRouter()

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "assessments.json")

def load_assessments():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@router.get("/")
async def get_assessments(skill: str = None, ks: str = None):
    data = load_assessments()
    if skill:
        data = [d for d in data if d.get("s") == skill]
    if ks:
        data = [d for d in data if d.get("ks") == ks]
    return data
