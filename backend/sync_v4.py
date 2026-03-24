import pandas as pd
import os, httpx, uuid
from typing import Dict, List
from dotenv import load_dotenv

SYL_ID = "ece00000-0000-0000-0000-000000000000"

def clean(s):
    return str(s).strip().strip("'").strip('"').lower()

def normalize_code(c):
    return "".join(x for x in str(c) if x.isalnum()).upper()

def sync_v4_gnostic():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    client = httpx.Client(headers=headers, timeout=60.0)
    
    # 0. Role
    role_id = 'e1d85bc3-a567-4354-9720-d3810237e100'

    # 1. Skill Nodes (from CSV)
    skill_csv = "d:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - Domain, skillset L C (9).csv"
    sdf = pd.read_csv(skill_csv).iloc[1:] 
    
    skill_desc_to_id = {}
    nodes = []
    for _, row in sdf.iterrows():
        desc = str(row.get('skill knowledge', '')).strip()
        if not desc or desc == 'nan': continue
        nodes.append({
            'job_role_id': role_id,
            'level': 'L1', 'concept': str(row.get('knowlegde set', 'Concept')).strip(),
            'skill_description': desc, 'domain': str(row.get('Domain', '')).strip(),
            'bloom_level': 1, 'common_tag': str(row.get('common tag ( try to make this based on subject)', '')).strip()
        })
    
    if nodes:
        print(f"Syncing {len(nodes)} Skill Nodes...")
        for i in range(0, len(nodes), 200):
            r = client.post(f"{url}/rest/v1/skill_nodes", json=nodes[i:i+200], headers={**headers, "Prefer": "return=representation, resolution=merge-duplicates"})
            if r.status_code in [200, 201]:
                for sn in r.json():
                    skill_desc_to_id[clean(sn['skill_description'])] = sn['id']

    # 2. Courses (from CO CSV)
    co_csv = "d:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - CO sheet.csv"
    codf = pd.read_csv(co_csv)
    
    course_code_to_id = {}
    norm_course_code_to_id = {}
    courses_to_upload = []
    for _, row in codf[['Course code ', 'Course']].drop_duplicates().iterrows():
        raw_code = str(row['Course code ']).strip()
        name = str(row['Course']).strip().strip('\n') 
        if not raw_code or raw_code == 'nan': continue
        
        cid = f"{SYL_ID}_{normalize_code(raw_code)[:20]}"
        courses_to_upload.append({'id': cid, 'syllabus_id': SYL_ID, 'course_code': raw_code, 'title': name, 'semester': 1, 'credits': 3})
        course_code_to_id[raw_code] = cid
        norm_course_code_to_id[normalize_code(raw_code)] = cid
    
    if courses_to_upload:
        print(f"Syncing {len(courses_to_upload)} Courses...")
        client.post(f"{url}/rest/v1/courses", json=courses_to_upload)

    # 3. Course Outcomes (from CO CSV)
    co_lookup = {}
    cos_to_upload = []
    for _, row in codf.iterrows():
        raw_code = str(row['Course code ']).strip()
        co_code = str(row['CO']).strip()
        desc = str(row['CO Description']).strip()
        cid = course_code_to_id.get(raw_code)
        if cid:
            co_id = f"{cid}_{co_code}"
            cos_to_upload.append({'id': co_id, 'course_id': cid, 'co_code': co_code, 'description': desc})
            co_lookup[(cid, co_code)] = co_id
    
    if cos_to_upload:
        print(f"Syncing {len(cos_to_upload)} Course Outcomes...")
        for i in range(0, len(cos_to_upload), 200):
            client.post(f"{url}/rest/v1/course_outcomes", json=cos_to_upload[i:i+200])

    # 4. Mappings (from Excel)
    ref_excel = "d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx"
    refdf = pd.read_excel(ref_excel)
    
    # Identify columns by content search
    code_col = None
    co_col = None
    skill_col = None
    
    for col in refdf.columns:
        scol = str(col).lower()
        if 'code' in scol or 'secondary' in scol and 'code' in scol: code_col = col
        if 'co' in scol and 'text' not in scol: co_col = col
        if 'skill' in scol: skill_col = col
    
    # Defaults based on previous audit if detection fails
    if not code_col: code_col = 'Secondary\nCode'
    if not co_col: co_col = 'Secondary\nCO'
    if not skill_col: skill_col = 'Skill Description'
    
    print(f"Using Columns: Code={repr(code_col)}, CO={repr(co_col)}, Skill={repr(skill_col)}")
    
    mappings = []
    print(f"Processing {len(refdf)} rows...")
    for _, row in refdf.iterrows():
        raw_code = str(row.get(code_col, '')).strip()
        co_code = str(row.get(co_col, '')).strip()
        skill_desc = clean(row.get(skill_col, ''))
        
        cid = norm_course_code_to_id.get(normalize_code(raw_code))
        sn_id = skill_desc_to_id.get(skill_desc)
        co_id = co_lookup.get((cid, co_code))
        
        if cid and sn_id and co_id:
            mappings.append({
                'syllabus_id': SYL_ID, 'course_id': cid, 'co_id': co_id,
                'skill_node_id': sn_id, 'match_type': 'manual', 'similarity_score': 1.0
            })
    
    print(f"Created {len(mappings)} mappings locally.")
    if mappings:
        client.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}")
        for i in range(0, len(mappings), 200):
            client.post(f"{url}/rest/v1/co_skill_mappings", json=mappings[i:i+200])
    
    print("Sync Done!")

if __name__ == "__main__":
    sync_v4_gnostic()
