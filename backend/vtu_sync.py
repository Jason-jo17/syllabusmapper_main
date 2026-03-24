import httpx, os, json
from dotenv import load_dotenv

# SYL_ID for the main ECE syllabus
SYL_ID = "ece00000-0000-0000-0000-000000000000"

def normalize(c):
    return "".join(x for x in str(c) if x.isalnum()).upper()

def clean(s):
    return str(s).strip().strip("'").strip('"').lower()

ID_MAPS = [
    # Skill desc -> (Course_ID, CO_Num)
    ("Calculating V, I, R in simple circuits using Ohm's Law -BL1", "3199da9f-159a-449c-971c-66c93318a4b7", "1"),
    ("Computing power dissipation in a resistor -BL1", "3199da9f-159a-449c-971c-66c93318a4b7", "2"),
    ("Identifying AC and DC sources in everyday devices -BL1", "3199da9f-159a-449c-971c-66c93318a4b7", "3"),
    ("Understanding how motors and transformers work (conceptual) -BL1", "3199da9f-159a-449c-971c-66c93318a4b7", "4"),
    ("Applying KVL/KCL to simple series-parallel circuits -BL2", "3199da9f-159a-449c-971c-66c93318a4b7", "5"),
    ("Identifying components by physical appearance and markings -BL1", "d8b50e2d-dc99-43ef-b387-052637738f64", "1"),
    ("Reading component datasheets for basic specs (voltage, current) -BL2", "d8b50e2d-dc99-43ef-b387-052637738f64", "2"),
    ("Building simple circuits on a breadboard (LED + resistor) -BL2", "d8b50e2d-dc99-43ef-b387-052637738f64", "3"),
    ("Measuring circuit parameters with a multimeter -BL2", "d8b50e2d-dc99-43ef-b387-052637738f64", "4"),
    ("Rearranging circuit equations to solve for voltage/current -BL2", "d8b50e2d-dc99-43ef-b387-052637738f61", "1"),
    ("Understanding sinusoidal waveform parameters (amplitude, frequency, phase) -BL2", "d8b50e2d-dc99-43ef-b387-052637738f61", "2"),
    ("Converting between binary, hex, and decimal for digital systems -BL2", "d8b50e2d-dc99-43ef-b387-052637738f62", "1")
]

def vtu_sync():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    client = httpx.Client(headers=headers, timeout=60.0)

    # 1. Fetch current DB state for Skills/COs
    print("Fetching DB state...")
    with open('db_state.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    skills = {clean(s['skill_description']): s['id'] for s in db['skills']}
    # handle both "1" and "CO1"
    cos_raw = db['cos']
    
    # 2. Build Mappings
    mappings = []
    skill_updates = []
    
    print(f"Checking {len(ID_MAPS)} mappings...")
    for desc, c_id, co_num in ID_MAPS:
        s_id = skills.get(clean(desc))
        
        # FIND CO (super robust)
        co_id = None
        target_digits = "".join(filter(str.isdigit, str(co_num)))
        for c in cos_raw:
            if c['course_id'] == c_id:
                code_raw = str(c.get('co_code', ''))
                code_digits = "".join(filter(str.isdigit, code_raw))
                if code_digits == target_digits:
                    co_id = c['id']
                    break
        
        if not co_id and s_id:
            # Debug: What are the COs for this course?
            avail = [str(c.get('co_code')) for c in cos_raw if c['course_id'] == c_id]
            print(f"DEBUG: Course {c_id} lacks CO {co_num}. Has: {avail}")
        
        if s_id and co_id:
            mappings.append({
                'syllabus_id': SYL_ID,
                'course_id': c_id,
                'co_id': co_id,
                'skill_node_id': s_id,
                'match_type': 'manual',
                'similarity_score': 1.0
            })
            
            # Fetch course title from db state to be precise
            c_info = next((c for c in db['courses'] if c['id'] == c_id), {})
            code = c_info.get('course_code', 'Unknown')
            from vtu_data import get_course_title
            title = get_course_title(code) or code

            skill_updates.append((s_id, {
                'co_primary_text': f"CO{co_num}: Mapped from VTU standard dataset",
                'co_primary_course': title,
                'co_primary_year': '1' if '1' in str(code) else '2',
                'co_primary_sem': '1' if '1' in str(code).split('/')[-1] else '3'
            }))
        else:
            print(f"MISSING: Skill '{desc[:20]}' Found={s_id is not None}, CO Found={co_id is not None} (Course {c_id[:8]})")

    # 3. Push to DB
    if mappings:
        print(f"Deleting 12 old mappings for syllabus {SYL_ID}...")
        client.delete(f"{url}/rest/v1/co_skill_mappings?syllabus_id=eq.{SYL_ID}")
        
        print(f"Pushing {len(mappings)} NEW mappings...")
        client.post(f"{url}/rest/v1/co_skill_mappings", json=mappings)

    print("Updating skill nodes with primary mapping info...")
    for s_id, data in skill_updates:
        client.patch(f"{url}/rest/v1/skill_nodes?id=eq.{s_id}", json=data)

    print("VTU Sync Finalized successfully!")

if __name__ == "__main__":
    vtu_sync()
