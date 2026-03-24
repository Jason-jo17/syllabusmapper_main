import pandas as pd
import os, httpx, json, re
from typing import Dict, List
from dotenv import load_dotenv

SYL_ID = "ece00000-0000-0000-0000-000000000000"

def clean(s):
    return str(s).strip().strip("'").strip('"').lower()

def normalize_code(c):
    return "".join(x for x in str(c) if x.isalnum()).upper()

def sync_v5():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    client = httpx.Client(headers=headers, timeout=60.0)

    with open('db_state.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    course_code_to_id = {normalize_code(c['course_code']): c['id'] for c in db['courses']}
    skill_desc_to_id = {clean(s['skill_description']): s['id'] for s in db['skills']}
    # Strip spaces from co_code in lookup build
    co_lookup = {(c['course_id'], str(c['co_code']).strip()): c['id'] for c in db['cos']}

    print(f"DB Context: {len(course_code_to_id)} courses, {len(skill_desc_to_id)} skills, {len(co_lookup)} COs.")

    ref_excel = "d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx"
    refdf = pd.read_excel(ref_excel, header=None)
    
    mappings = []
    skill_updates = {}

    active_p = None # (norm, id)
    active_s = None
    active_t = None

    print("Parsing Excel with Row-by-Row Debug...")
    for i, row in refdf.iterrows():
        # Check for course code updates
        for col_idx in [11, 16, 21]:
            val = str(row[col_idx]).strip()
            norm = normalize_code(val)
            if norm in course_code_to_id:
                if col_idx == 11: active_p = (norm, course_code_to_id[norm])
                if col_idx == 16: active_s = (norm, course_code_to_id[norm])
                if col_idx == 21: active_t = (norm, course_code_to_id[norm])
                # print(f"Row {i}: New active course in col {col_idx}: {norm}")

        skill_text = clean(row[5])
        if skill_text in skill_desc_to_id:
            sn_id = skill_desc_to_id[skill_text]
            
            # Use columns 11, 16, 21 for COs
            for col_idx, active_course, kind in [(11, active_p, 'primary'), (16, active_s, 'secondary'), (21, active_t, 'tertiary')]:
                co_val = str(row[col_idx]).strip()
                if active_course and re.match(r'^CO\d+$', co_val):
                    cid = active_course[1]
                    coid = co_lookup.get((cid, co_val))
                    if coid:
                        mappings.append({
                            'syllabus_id': SYL_ID, 'course_id': cid, 'co_id': coid,
                            'skill_node_id': sn_id, 'match_type': 'manual', 'similarity_score': 1.0
                        })
                        
                        update = skill_updates.get(sn_id, {})
                        from vtu_data import get_course_title
                        title = get_course_title(active_course[0]) or active_course[0]
                        update[f'co_{kind}_text'] = f"{co_val}: [Excel Mapping]"
                        update[f'co_{kind}_course'] = title
                        skill_updates[sn_id] = update
                    else:
                        if i < 10: print(f"Row {i}: CO lookup failed for {(active_course[0], co_val)}")

    print(f"Parsed {len(mappings)} mappings.")

    if mappings:
        client.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}")
        unique_mappings = {(m['co_id'], m['skill_node_id']): m for m in mappings}
        dedup = list(unique_mappings.values())
        print(f"Deduplicated to {len(dedup)} mappings.")
        for i in range(0, len(dedup), 200):
            r = client.post(f"{url}/rest/v1/co_skill_mappings", json=dedup[i:i+200])
            if r.status_code >= 400: print(f"Error {r.status_code}: {r.text}")

    if skill_updates:
        print(f"Patching {len(skill_updates)} Skill Nodes...")
        for sn_id, data in skill_updates.items():
            client.patch(f"{url}/rest/v1/skill_nodes?id=eq.{sn_id}", json=data)

    print("Sync v5 Debug Complete!")

if __name__ == "__main__":
    sync_v5()
