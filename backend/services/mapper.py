import google.generativeai as genai
import json
import os, httpx
from typing import List

def _get_api_config():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '')
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    return url, h

_model = None
def get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model

RERANK_SYSTEM = """You are an expert curriculum mapper. 
Given a Course Outcome (CO) and a list of Skill Nodes (candidates from vector search), 
select the BEST matches (up to 3). 
Return ONLY a JSON array of skill_node_ids."""

async def map_co(co_id, co_desc, course_title, embedding, syllabus_id, course_id):
    url, h = _get_api_config()
    if not url: return []
    model = get_model()
    # 1. Vector Search for Candidates
    rpc_url = f"{url}/rest/v1/rpc/match_skill_nodes"
    try:
        r = httpx.post(rpc_url, headers=h, json={
            'query_embedding': embedding, 'match_threshold': 0.5, 'match_count': 15
        }, timeout=30.0)
        
        if r.status_code != 200: return []
        candidates = r.json()
        if not candidates: return []
        
        # 2. Rerank with AI
        prompt = f"Course: {course_title}\nCO: {co_desc}\n\nCandidates:\n"
        for c in candidates:
            prompt += f"- ID: {c['id']}, Concept: {c['concept']}, Description: {c['skill_description']}\n"
        
        response = model.generate_content(RERANK_SYSTEM + "\n\n" + prompt)
        text = response.text.strip()
        # Clean potential markdown
        if '```' in text:
            text = text.split('```')[1].replace('json', '').strip()
        
        best_ids = json.loads(text)
        if not isinstance(best_ids, list): best_ids = []
        
        # 3. Save to DB
        for sn_id in best_ids:
            httpx.post(f"{url}/rest/v1/co_skill_mappings", headers=h, json={
                'syllabus_id': syllabus_id, 'course_id': course_id, 'co_id': co_id,
                'skill_node_id': sn_id, 'match_type': 'ai', 'similarity_score': 1.0
            }, timeout=10.0)
        return best_ids
    except Exception as e:
        print(f"Rerank/Save error: {e}")
        return []

async def map_syllabus_cos(syllabus_id):
    url, h = _get_api_config()
    if not url: return
    try:
        r = httpx.get(f"{url}/rest/v1/courses?syllabus_id=eq.{syllabus_id}&select=id,title", headers=h, timeout=20.0)
        if r.status_code != 200: return
        courses = r.json()
        
        for course in courses:
            r = httpx.get(f"{url}/rest/v1/course_outcomes?course_id=eq.{course['id']}&select=*", headers=h, timeout=20.0)
            if r.status_code == 200:
                cos = r.json()
                for co in cos:
                    if co.get('embedding'):
                        await map_co(co['id'], co['description'], course['title'], co['embedding'], syllabus_id, course['id'])
    except Exception as e:
        print(f"Mapping syllabus error: {e}")
