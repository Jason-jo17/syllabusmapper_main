import pandas as pd
import os
import httpx
from dotenv import load_dotenv

SYL_ID = "ece00000-0000-0000-0000-000000000000"

def sync_v2():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    
    client = httpx.Client(headers=headers, timeout=60.0)
    
    excel_path = "d:/Downloads2/syllabusmapper/backend/data/ECE_L0L5_VTU_CO_v2.xlsx"
    df = pd.read_excel(excel_path)
    
    # Aggressive clean
    new_cols = []
    for c in df.columns:
        sc = str(c).replace('\n', ' ').strip().strip("'")
        # remove quotes from both ends again if they were nested
        while (sc.startswith("'") and sc.endswith("'")) or (sc.startswith('"') and sc.endswith('"')):
            sc = sc[1:-1].strip()
        new_cols.append(sc)
    df.columns = new_cols
    
    print(f"Loaded {len(df)} rows.")
    print(f"CLEANED COLS REPR: {[repr(c) for c in df.columns]}")
    if len(df) > 0:
        print(f"ROW 1: {df.iloc[0].to_dict()}")

    # 1. Role
    r = client.get(f"{url}/rest/v1/job_roles?role_name=eq.Embedded Electronics Engineer&select=id").json()
    role_id = r[0]['id']

    # 2. Courses
    try:
        unique_courses = df[['Course code', 'Course name', 'Sem']].drop_duplicates().dropna(subset=['Course code'])
    except Exception as e:
        print(f"FAIL ON SUBSET: {e}")
        # Try to find columns by partial match
        code_col = [c for c in df.columns if 'Course code' in c][0]
        name_col = [c for c in df.columns if 'Course name' in c][0]
        sem_col = [c for c in df.columns if 'Sem' in c][0]
        unique_courses = df[[code_col, name_col, sem_col]].drop_duplicates().dropna(subset=[code_col])
        # Update column names for iteration
        unique_courses.columns = ['Course code', 'Course name', 'Sem']

    print(f"Upserting {len(unique_courses)} courses...")
    course_code_to_id = {}
    for _, row in unique_courses.iterrows():
        code = str(row['Course code']).strip().strip("'")
        name = str(row['Course name']).strip().strip("'")
        sem_val = row['Sem']
        sem = int(sem_val) if not pd.isna(sem_val) else 1
        safe_code = "".join(x for x in code if x.isalnum())
        cid = f"{SYL_ID}_{safe_code[:20]}"
        client.post(f"{url}/rest/v1/courses", json={
            'id': cid, 'syllabus_id': SYL_ID, 'course_code': code, 'title': name, 'semester': sem, 'credits': 3
        })
        course_code_to_id[code] = cid
    
    # 3. COs
    # Mapping
    co_col = [c for c in df.columns if 'CO_Text_Lookup' in c][0]
    unique_cos = df[[code_col, co_col]].drop_duplicates().dropna()
    print(f"Upserting COs...")
    co_lookup = {}
    for _, row in unique_cos.iterrows():
        code = str(row[code_col]).strip().strip("'")
        co_code = str(row[co_col]).strip().strip("'")
        cid = course_code_to_id.get(code)
        if cid:
            co_id = f"{cid}_{co_code}"
            desc = f"Learning outcome for {code} ({co_code})"
            client.post(f"{url}/rest/v1/course_outcomes", json={
                'id': co_id, 'course_id': cid, 'co_code': co_code, 'description': desc
            })
            co_lookup[(cid, co_code)] = co_id

    # 4. Skills
    skill_col = 'Skill Description'
    unique_skills = df[[skill_col, 'Level', 'Common Tag', 'Primary Concept', 'Tools']].drop_duplicates().dropna(subset=[skill_col])
    print(f"Upserting {len(unique_skills)} skill nodes...")
    skill_desc_to_id = {}
    for _, row in unique_skills.iterrows():
        desc = str(row[skill_col]).strip().strip("'")
        node = {
            'job_role_id': role_id,
            'level': str(row['Level']).strip(),
            'concept': str(row['Primary Concept']).strip(),
            'skill_description': desc,
            'tools': str(row['Tools']).strip() if not pd.isna(row['Tools']) else "",
            'common_tag': str(row['Common Tag']).strip() if not pd.isna(row['Common Tag']) else "",
            'co_primary_course': str(row.get('Course name', '')).strip(),
            'co_primary_text': str(row.get('CO_Text_Lookup', '')).strip(),
            'co_primary_year': str(row.get('Year', '')).strip(),
            'co_primary_sem': str(row.get('Sem', '')).strip()
        }
        r = client.post(f"{url}/rest/v1/skill_nodes", json=node, headers={"Prefer": "return=representation, resolution=merge-duplicates"})
        if r.status_code in [200, 201]:
             skill_desc_to_id[desc] = r.json()[0]['id']
    
    # 5. Mappings
    print("Recreating mappings...")
    client.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}")
    mappings = []
    for _, row in df.iterrows():
        code = str(row.get(code_col, '')).strip().strip("'")
        co_code = str(row.get(co_col, '')).strip().strip("'")
        skill_desc = str(row.get(skill_col, '')).strip().strip("'")
        cid = course_code_to_id.get(code)
        sn_id = skill_desc_to_id.get(skill_desc)
        co_id = co_lookup.get((cid, co_code))
        if cid and sn_id and co_id:
            mappings.append({
                'syllabus_id': SYL_ID, 'course_id': cid, 'co_id': co_id,
                'skill_node_id': sn_id, 'match_type': 'manual', 'similarity_score': 1.0
            })
    if mappings:
        for i in range(0, len(mappings), 50):
            client.post(f"{url}/rest/v1/co_skill_mappings", json=mappings[i:i+50])
    print(f"Done! Created {len(mappings)} mappings.")

if __name__ == "__main__":
    sync_v2()
