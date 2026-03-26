import csv, asyncio, os, json, uuid, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client
from services.embedder import batch_embed

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')
sb = create_client(url, key)

async def seed_ece_curriculum():
    csv_path = 'data/Event Mastersheet mockup - CO sheet.csv'
    if not os.path.exists(csv_path):
         csv_path = os.path.join(os.path.dirname(__file__), 'Event Mastersheet mockup - CO sheet.csv')
    
    syl_id = "ece00000-0000-0000-0000-000000000000"
    col_id = "00000000-0000-0000-0000-000000000000"
    
    print(f"Ensuring Syllabus {syl_id} exists...")
    sb.table('syllabi').upsert({
        'id': syl_id, 'college_id': col_id, 'stream': 'Embedded Electronics', 'regulation': '2024',
        'title': 'VTU ECE Curriculum', 'source_type': 'csv', 'ingestion_status': 'completed'
    }, on_conflict='id').execute()

    # Deep cleanup using syllabus_id
    print("Performing deep cleanup...")
    # 1. Delete mappings (linked to syllabus_id)
    sb.table('co_skill_mappings').delete().eq('syllabus_id', syl_id).execute()
    # 2. Delete outcomes (via course syllabus link)
    course_res = sb.table('courses').select('id').eq('syllabus_id', syl_id).execute()
    existing_course_ids = [c['id'] for c in course_res.data]
    if existing_course_ids:
        sb.table('course_outcomes').delete().in_('course_id', existing_course_ids).execute()
        sb.table('courses').delete().in_('id', existing_course_ids).execute()

    courses_map = {} # code -> course_data
    all_rows = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [fn.strip() for fn in reader.fieldnames]
        
        for row_raw in reader:
            row = {k.strip(): v.strip() for k, v in row_raw.items()}
            if row.get('stream', '') != 'ECE': continue
            
            code = row.get('Course code')
            name = row.get('Course')
            yr_str = row.get('year', '').lower()
            sem_str = row.get('sem', '').lower()
            if not code or not name: continue
            
            # Robust extraction (e.g. "4th year" -> 4, "7th sem" -> 7)
            import re
            year = 2
            match_yr = re.search(r'(\d+)', yr_str)
            if match_yr: year = int(match_yr.group(1))
            
            sem = 3
            match_sem = re.search(r'(\d+)', sem_str)
            if match_sem: sem = int(match_sem.group(1))
            
            if code not in courses_map:
                courses_map[code] = {
                    'id': str(uuid.uuid4()),
                    'syllabus_id': syl_id, 'college_id': col_id,
                    'course_code': code, 'course_title': name,
                    'year_of_study': year, 'semester': sem, 'credits': 4
                }
            all_rows.append(row)

    print(f"Inserting {len(courses_map)} courses...")
    course_list = list(courses_map.values())
    for i in range(0, len(course_list), 50):
        sb.table('courses').insert(course_list[i:i+50]).execute()

    # Pre-fetch to verify
    db_courses = sb.table('courses').select('id').eq('syllabus_id', syl_id).execute()
    db_ids = {c['id'] for c in db_courses.data}
    print(f"Verified {len(db_ids)} courses in DB.")

    texts_to_embed = []
    cos_data = [] # (course_id, co_code, description)
    for r in all_rows:
        code = r['Course code']
        co_code = r['CO']
        desc = r['CO Description']
        if not desc or code not in courses_map: continue
        
        cid = courses_map[code]['id']
        if cid not in db_ids:
            print(f"WARNING: Course ID {cid} (Code {code}) missing from DB verification!")
            continue
            
        texts_to_embed.append(desc)
        cos_data.append((cid, co_code, desc))

    print(f"Embedding {len(texts_to_embed)} outcomes...")
    embeddings = await batch_embed(texts_to_embed)
    
    co_inserts = []
    for (cid, co_code, desc), emb in zip(cos_data, embeddings):
        co_id = str(uuid.uuid4())
        co_inserts.append({
            'id': co_id, 'course_id': cid, 'co_code': co_code,
            'description': desc, 'embedding': emb
        })

    print(f"Inserting {len(co_inserts)} outcomes...")
    for i in range(0, len(co_inserts), 50):
        sb.table('course_outcomes').insert(co_inserts[i:i+50]).execute()

    print(f"Mapping Course Outcomes to Skills (with throttling)...")
    mapping_inserts = []
    for co in co_inserts:
        course_name = courses_map[next(k for k,v in courses_map.items() if v['id'] == co['course_id'])]['course_title'].lower()
        
        # Determine target domain
        is_general = any(kw in course_name for kw in ['biology', 'social', 'management', 'uhv', 'english', 'kannada', 'connect', 'universal'])
        target_domain = None if is_general else 'Embedded systems'
        
        try:
            res = sb.rpc('match_skill_nodes', {
                'query_embedding': co['embedding'],
                'match_threshold': 0.45 if is_general else 0.5,
                'match_count': 3,
                'filter_domain': target_domain
            }).execute()
            
            for m in res.data:
                mapping_inserts.append({
                    'syllabus_id': syl_id, 'course_id': co['course_id'], 'co_id': co['id'],
                    'skill_node_id': m['id'], 'similarity_score': m['similarity'], 'match_type': 'vector_match'
                })
        except Exception as e:
            print(f"  - WARNING: Failed to map CO {co['co_code']} for {course_name}: {e}")
            
        # Throttling to prevent XX000 internal server error
        await asyncio.sleep(0.05)

    print(f"Inserting {len(mapping_inserts)} mappings...")
    for i in range(0, len(mapping_inserts), 50):
        sb.table('co_skill_mappings').insert(mapping_inserts[i:i+50]).execute()

    print("ECE Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed_ece_curriculum())
