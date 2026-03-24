import pandas as pd
import os
import uuid
import httpx
from dotenv import load_dotenv

SYL_ID = "ece00000-0000-0000-0000-000000000000"

def sync_batch():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    
    excel_path = "d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx"
    df = pd.read_excel(excel_path)
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
    
    print(f"Loaded {len(df)} rows.")
    print(f"COLS: {list(df.columns)}")
    if not df.empty:
        print(f"ROW 1: {df.iloc[0].to_dict()}")
    else:
        print("EMPTY DF")

    # 1. Get Role ID
    r = httpx.get(f"{url}/rest/v1/job_roles?role_name=eq.Domain Skills Mapping&select=id", headers=headers).json()
    if not r:
        r = httpx.get(f"{url}/rest/v1/job_roles?role_name=ilike.*Embedded*&select=id", headers=headers).json()
    if not r:
        print("Role not found")
        return
    role_id = r[0]['id']

    # 2. Extract and Upsert Courses and COs from Excel
    print("Syncing Courses and COs from Excel...")
    unique_cos = {} # (cname, co_code) -> desc
    for _, row in df.iterrows():
        cnames = [str(row.get(f'{p} Course', '')).strip() for p in ['Primary', 'Secondary', 'Tertiary']]
        codes = [str(row.get(f'{p} CO', '')).strip() for p in ['Primary', 'Secondary', 'Tertiary']]
        desc = str(row.get('CO Description', '')).strip()
        
        for cname, co_code in zip(cnames, codes):
            if cname and cname != 'nan' and cname != '—' and co_code and co_code != 'nan':
                unique_cos[(cname, co_code)] = desc
    
    unique_excel_courses = {c[0] for c in unique_cos.keys()}
    for cname in unique_excel_courses:
        safe_name = "".join(x for x in cname if x.isalnum())
        cid = f"{SYL_ID}_{safe_name[:20]}"
        httpx.post(f"{url}/rest/v1/courses", headers=headers, json={'id': cid, 'syllabus_id': SYL_ID, 'title': cname, 'course_code': 'MAPPED'})
    
    # Refresh Courses
    r = httpx.get(f"{url}/rest/v1/courses?syllabus_id=eq.{SYL_ID}&select=*", headers=headers)
    courses = r.json()
    if not isinstance(courses, list):
        print(f"Error fetching courses: {courses}")
        return
    if courses:
        print(f"FIRST COURSE KEYS: {list(courses[0].keys())}")
    course_name_to_id = {str(c.get('title', '')).strip(): c['id'] for c in courses if c.get('title')}
    print(f"DEBUG: Found {len(course_name_to_id)} courses in lookup.")
    if course_name_to_id:
         print(f"DEBUG: Sample courses in lookup: {list(course_name_to_id.keys())[:3]}")
    
    # Upsert COs
    print(f"Upserting {len(unique_cos)} unique CO descriptions...")
    for (cname, co_code), desc in unique_cos.items():
        cid = course_name_to_id.get(cname)
        if cid:
            co_id = f"{cid}_{co_code}"
            httpx.post(f"{url}/rest/v1/course_outcomes", headers=headers, json={
                'id': co_id, 'course_id': cid, 'co_code': co_code, 'description': desc
            })

    # 4. Refresh CO lookup
    r = httpx.get(f"{url}/rest/v1/course_outcomes?select=*", headers=headers)
    cos = r.json()
    if not isinstance(cos, list):
         print(f"Error fetching COs: {cos}")
         return
    co_lookup = {(c['course_id'], str(c['co_code']).strip()): c['id'] for c in cos}
    print(f"DEBUG: Found {len(co_lookup)} COs in lookup.")
    if co_lookup:
         print(f"DEBUG: Sample CO keys: {list(co_lookup.keys())[:3]}")

    # 5. Clear old mappings
    httpx.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}", headers=headers)

    skill_nodes_to_upsert = []
    mappings_to_insert = []

    for _, row in df.iterrows():
        skill_desc = str(row.get('Skill Description', '')).strip()
        if not skill_desc or skill_desc == "nan": continue

        node = {
            'job_role_id': role_id,
            'level': str(row.get('Level', '')).strip(),
            'knowledge_set': str(row.get('knowlegde set', '')).strip(),
            'concept': str(row.get('Skill Concept', '')).strip(),
            'skill_description': skill_desc,
            'bloom_level': int(row['BL']) if not pd.isna(row.get('BL')) else 0,
            'common_tag': str(row.get('Common Tag', '')),
            'domain': str(row.get('Domain', '')),
            'category': str(row.get('Category', '')),
            'co_primary_course': str(row.get('Primary Course', '')).strip(),
            'co_primary_text': str(row.get('Primary CO', '')).strip(),
            'co_primary_year': str(row.get('Primary Year', '')),
            'co_primary_sem': str(row.get('Primary Sem', '')),
            'co_secondary_course': str(row.get('Secondary Course', '')).strip(),
            'co_secondary_text': str(row.get('Secondary CO', '')).strip(),
            'co_secondary_year': str(row.get('Secondary Year', '')),
            'co_secondary_sem': str(row.get('Secondary Sem', '')),
            'co_tertiary_course': str(row.get('Tertiary Course', '')).strip(),
            'co_tertiary_text': str(row.get('Tertiary CO', '')).strip(),
            'co_tertiary_year': str(row.get('Tertiary Year', '')),
            'co_tertiary_sem': str(row.get('Tertiary Sem', ''))
        }
        skill_nodes_to_upsert.append(node)

    print(f"Collected {len(skill_nodes_to_upsert)} skill nodes to upsert.")

    # Upsert Skill Nodes
    if skill_nodes_to_upsert:
        print(f"Upserting {len(skill_nodes_to_upsert)} skill nodes...")
        for i in range(0, len(skill_nodes_to_upsert), 50):
             # Try POST with upsert preference
             r = httpx.post(f"{url}/rest/v1/skill_nodes", headers=headers, json=skill_nodes_to_upsert[i:i+50])
             if r.status_code not in [200, 201]:
                 print(f"Error upserting nodes: {r.status_code} {r.text}")
    
    # Re-retrieve IDs to create mappings
    all_sn = httpx.get(f"{url}/rest/v1/skill_nodes?job_role_id=eq.{role_id}&select=id,skill_description", headers=headers).json()
    desc_to_sn_id = {str(s['skill_description']).strip(): s['id'] for s in all_sn}
    print(f"Found {len(desc_to_sn_id)} skill nodes in DB for mapping.")

    for _, row in df.iterrows():
        desc = str(row.get('Skill Description', '')).strip()
        sn_id = desc_to_sn_id.get(desc)
        if not sn_id: 
            # try fuzzy match or case-insensitive if needed
            continue

        matched_c = 0
        for prefix in ['Primary', 'Secondary', 'Tertiary']:
            course = str(row.get(f'{prefix} Course', '')).strip()
            co = str(row.get(f'{prefix} CO', '')).strip()
            if course and course != "nan" and course != "—":
                if course in course_name_to_id:
                    matched_c += 1
                    cid = course_name_to_id[course]
                    co_id = co_lookup.get((str(cid).strip(), str(co).strip()))
                    if co_id:
                        mappings_to_insert.append({
                            'syllabus_id': SYL_ID, 'course_id': cid, 'co_id': co_id,
                            'skill_node_id': sn_id, 'match_type': 'manual', 'similarity_score': 1.0
                        })
                    else:
                        if not hasattr(sync_batch, "fail_co"):
                             print(f"DEBUG: CO FAIL {co} for {course} ({cid})")
                             sync_batch.fail_co = True
                else:
                    if not hasattr(sync_batch, "fail_course"):
                         print(f"DEBUG: COURSE FAIL {course}")
                         sync_batch.fail_course = True
        if matched_c > 0:
             if not hasattr(sync_batch, "success_c"):
                  print(f"DEBUG: SUCCESS COURSE MATCH for {desc[:20]}")
                  sync_batch.success_c = True
    
    print(f"Collected {len(mappings_to_insert)} mappings to insert.")
    m_headers = headers.copy()
    m_headers["Prefer"] = "return=representation"
    for i in range(0, len(mappings_to_insert), 50):
        r = httpx.post(f"{url}/rest/v1/co_skill_mappings", headers=m_headers, json=mappings_to_insert[i:i+50])
        if r.status_code not in [200, 201]:
             print(f"Error inserting mappings: {r.status_code} {r.text}")
        else:
             print(f"Successfully inserted batch {i//50}, first item: {r.json()[0] if r.json() else 'EMPTY'}")

    print("Done!")

if __name__ == "__main__":
    sync_batch()
