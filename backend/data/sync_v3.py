import pandas as pd
import os, httpx, uuid
from typing import Dict, List
from dotenv import load_dotenv

SYL_ID = "ece00000-0000-0000-0000-000000000000"

def clean(s):
    return str(s).strip().strip("'").strip('"').lower()

def sync_v3_fully_robust():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    client = httpx.Client(headers=headers, timeout=60.0)
    
    # 0. Ensure Role and Syllabus
    print("Ensuring Job Role and Syllabus exist...")
    role_name = "Embedded Electronics Engineer"
    r_role = client.post(f"{url}/rest/v1/job_roles", json={'role_name': role_name}, headers={**headers, "Prefer": "return=representation, resolution=merge-duplicates"})
    role_id = r_role.json()[0]['id']
    
    client.post(f"{url}/rest/v1/syllabi", json={
        'id': SYL_ID, 'title': 'ECE Final Syllabus (Reference)', 'college_id': 'vtu-university-id-001'
    })

    # 1. Skill Nodes
    skill_csv = "d:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - Domain, skillset L C (9).csv"
    sdf = pd.read_csv(skill_csv)
    sdf.columns = [str(c).strip() for c in sdf.columns]
    
    print(f"Syncing {len(sdf)} Skill Nodes...")
    skill_desc_to_id = {}
    for _, row in sdf.iterrows():
        desc = str(row['l5 skill description']).strip()
        if not desc or desc == 'nan': continue
        
        node = {
            'job_role_id': role_id,
            'level': str(row.get('l4 concept', 'L1')).strip()[:2], # Truncate to L0-L5
            'concept': str(row.get('l4 concept', 'Concept')),
            'skill_description': desc,
            'domain': f"{row.get('L0 domain', '')} > {row.get('l1 domain', '')}",
            'category': str(row.get('l2 category', '')),
            'knowledge_set': str(row.get('l3 knowledge set', '')),
            'bloom_level': int(row['bloom level']) if not pd.isna(row.get('bloom level')) else 0,
            'common_tag': str(row.get('common tag ( try to make this consistent )', ''))
        }
        r = client.post(f"{url}/rest/v1/skill_nodes", json=node, headers={"Prefer": "return=representation, resolution=merge-duplicates"})
        if r.status_code in [200, 201]:
            skill_desc_to_id[clean(desc)] = r.json()[0]['id']

    # 2. Courses
    co_csv = "d:/Downloads2/syllabusmapper/backend/data/Event Mastersheet mockup - CO sheet.csv"
    codf = pd.read_csv(co_csv)
    codf.columns = [str(c).strip() for c in codf.columns]
    
    unique_courses = codf[['Course code', 'Course name']].drop_duplicates()
    print(f"Syncing {len(unique_courses)} Courses...")
    course_code_to_id = {}
    for _, row in unique_courses.iterrows():
        code = str(row['Course code']).strip()
        name = str(row['Course name']).strip()
        # Ensure ID format is robust
        clean_code = "".join(x for x in code if x.isalnum())
        cid = f"{SYL_ID}_{clean_code[:20]}" 
        client.post(f"{url}/rest/v1/courses", json={
            'id': cid, 'syllabus_id': SYL_ID, 'course_code': code, 'title': name, 'semester': 1, 'credits': 3
        })
        course_code_to_id[code] = cid
        
    print(f"Syncing {len(codf)} Course Outcomes...")
    co_lookup = {}
    for _, row in codf.iterrows():
        code = str(row['Course code']).strip()
        co_code = str(row['CO']).strip()
        desc = str(row['CO Description']).strip()
        cid = course_code_to_id.get(code)
        if cid:
            co_id = f"{cid}_{co_code}"
            client.post(f"{url}/rest/v1/course_outcomes", json={
                'id': co_id, 'course_id': cid, 'co_code': co_code, 'description': desc
            })
            co_lookup[(cid, co_code)] = co_id

    # 3. Mappings
    ref_excel = "d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx"
    refdf = pd.read_excel(ref_excel)
    refdf.columns = [str(c).replace('\n', ' ').strip().strip("'") for c in refdf.columns]
    
    print(f"Establishing {len(refdf)} Reference Mappings...")
    client.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}")
    
    mappings = []
    for _, row in refdf.iterrows():
        code = str(row.get('Course code', '')).strip().strip("'")
        co_code = str(row.get('CO_Text_Lookup', '')).strip().strip("'")
        skill_desc = clean(row.get('Skill Description', ''))
        
        cid = course_code_to_id.get(code)
        sn_id = skill_desc_to_id.get(skill_desc)
        co_id = co_lookup.get((cid, co_code))
        
        if cid and sn_id and co_id:
            mappings.append({
                'syllabus_id': SYL_ID, 'course_id': cid, 'co_id': co_id,
                'skill_node_id': sn_id, 'match_type': 'manual', 'similarity_score': 1.0
            })
            client.patch(f"{url}/rest/v1/skill_nodes?id=eq.{sn_id}", json={
                'co_primary_course': str(row.get('Course name', '')).strip(),
                'co_primary_text': co_code
            })
    
    if mappings:
        for i in range(0, len(mappings), 50):
            client.post(f"{url}/rest/v1/co_skill_mappings", json=mappings[i:i+50])

    print(f"Done! Created {len(mappings)} mappings.")

if __name__ == "__main__":
    sync_v3_fully_robust()
