import google.generativeai as genai
import json
import os, httpx
from typing import Optional

URL = os.environ.get('SUPABASE_URL')
KEY = os.environ.get('SUPABASE_KEY')
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

_model = None
def get_model():
    global _model
    if _model is None:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model

async def analyse(syllabus_id: str, job_role_id: str):
    # 1. Fetch total skills
    r = httpx.get(f"{URL}/rest/v1/skill_nodes?job_role_id=eq.{job_role_id}&select=*", headers=HEADERS)
    if r.status_code != 200: return {}
    total_skills = r.json()

    # 2. Fetch mapped skills
    r = httpx.get(f"{URL}/rest/v1/co_skill_mappings?syllabus_id=eq.{syllabus_id}&select=skill_node_id", headers=HEADERS)
    if r.status_code != 200: return {}
    mapped_ids = set(m['skill_node_id'] for m in r.json())

    missing = [s for s in total_skills if s['id'] not in mapped_ids]
    
    if not missing:
        report = {"total_skills": len(total_skills), "covered_skills": len(total_skills), "coverage_pct": 100.0, "gaps": [], "priority_gaps": []}
        # Save to DB
        httpx.post(f"{URL}/rest/v1/gap_reports", headers=HEADERS, json={
            'syllabus_id': syllabus_id, 'job_role_id': job_role_id, 'report_data': report
        })
        return report

    # 3. Priority analysis with Gemini
    clist = [{'id': s['id'], 'level': s['level'], 'concept': s['concept'], 'desc': s['skill_description']} for s in missing[:40]]
    model = get_model()
    
    prompt = f"""Identify priority gaps (Critical/High/Medium). 
L2/L3 skill gaps are usually Critical. 
Return ONLY JSON: {{"priority_gaps": [{{"skill_id": "...", "priority": "Critical", "reason": "..."}}]}}
Missing skills: {json.dumps(clist)}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if '```' in text: text = text.split('```')[1].replace('json', '').strip()
        result = json.loads(text)
    except Exception as e:
        print(f"GenAI Gap error: {e}")
        result = {"priority_gaps": []}
    
    report = {
        "total_skills": len(total_skills),
        "covered_skills": len(total_skills) - len(missing),
        "coverage_pct": ((len(total_skills) - len(missing)) / len(total_skills)) * 100 if total_skills else 0,
        "gaps": missing,
        "priority_gaps": result.get('priority_gaps', [])
    }
    
    # 4. Save to DB (Upsert)
    httpx.post(f"{URL}/rest/v1/gap_reports", headers={**HEADERS, "Prefer": "resolution=merge-duplicates"}, json={
        'id': f"{syllabus_id}_{job_role_id}",
        'syllabus_id': syllabus_id, 'job_role_id': job_role_id, 'report_data': report
    })
    
    return report
