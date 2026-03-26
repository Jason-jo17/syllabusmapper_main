import csv, asyncio, os, json, uuid, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client
from services.embedder import batch_embed

sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

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

    # Clear existing to re-seed
    print("Clearing existing ECE mappings and courses...")
    sb.table('co_skill_mappings').delete().eq('syllabus_id', syl_id).execute()
    sb.table('courses').delete().eq('syllabus_id', syl_id).execute()

    courses_to_insert = {} # code -> data
    all_rows = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Clean headers (handle trailing spaces like 'stream ')
        reader.fieldnames = [fn.strip() for fn in reader.fieldnames]
        
        for row_raw in reader:
            row = {k.strip(): v.strip() for k, v in row_raw.items()}
            stream = row.get('stream', '')
            if stream != 'ECE': continue
            
            code = row['Course code']
            name = row['Course']
            sem_str = row['sem'].lower()
            
            sem = 1
            if '1st' in sem_str or '2nd' in sem_str: sem = 1
            elif '3rd' in sem_str: sem = 3
            elif '4th' in sem_str: sem = 4
            elif '5th' in sem_str: sem = 5
            elif '6th' in sem_str: sem = 6
            elif '7th' in sem_str: sem = 7
            elif '8th' in sem_str: sem = 8
            
            if code not in courses_to_insert:
                cid = str(uuid.uuid4())
                courses_to_insert[code] = {
                    'id': cid, 
                    'syllabus_id': syl_id, 
                    'college_id': col_id,
                    'course_code': code, 
                    'course_title': name, 
                    'semester': sem, 
                    'credits': 4
                }
            all_rows.append(row)

    print(f"Inserting {len(courses_to_insert)} unique ECE courses...")
    course_list = list(courses_to_insert.values())
    for i in range(0, len(course_list), 50):
        sb.table('courses').insert(course_list[i:i+50]).execute()

    print(f"Processing ALL Course Outcomes for {len(all_rows)} entries...")
    texts_to_embed = []
    cos_to_process = []
    
    for r in all_rows:
        code = r['Course code']
        co_code = r['CO']
        desc = r['CO Description']
        if not desc or code not in courses_to_insert: continue
        
        texts_to_embed.append(desc)
        cos_to_process.append((courses_to_insert[code]['id'], co_code, desc))

    print(f"Embedding {len(texts_to_embed)} CO descriptions in batches...")
    embeddings = await batch_embed(texts_to_embed)
    
    co_inserts = []
    for (cid, co_code, desc), emb in zip(cos_to_process, embeddings):
        co_id = str(uuid.uuid4())
        co_inserts.append({
            'id': co_id, 'course_id': cid, 'co_code': co_code, 
            'description': desc, 'embedding': emb
        })

    if co_inserts:
        print(f"Inserting {len(co_inserts)} Course Outcomes...")
        for i in range(0, len(co_inserts), 50):
            sb.table('course_outcomes').insert(co_inserts[i:i+50]).execute()

    print("Generating CO-to-Skill mappings using vector search...")
    # This might take a while for 150+ COs
    mapping_inserts = []
    for co in co_inserts:
        # RPC to match_skill_nodes with domain filter to avoid cross-pollution
        matches = sb.rpc('match_skill_nodes', {
            'query_embedding': co['embedding'],
            'match_threshold': 0.5, # Lower threshold slightly for better coverage
            'match_count': 3,
            'filter_domain': 'Embedded systems'
        }).execute()
        
        for m in matches.data:
            mapping_inserts.append({
                'syllabus_id': syl_id,
                'course_id': co['course_id'],
                'co_id': co['id'],
                'skill_node_id': m['id'],
                'similarity_score': m['similarity'],
                'match_type': 'vector_match'
            })

    if mapping_inserts:
        print(f"Inserting {len(mapping_inserts)} skill mappings...")
        for i in range(0, len(mapping_inserts), 50):
            sb.table('co_skill_mappings').insert(mapping_inserts[i:i+50]).execute()

    print("ECE Curriculum Seeding and Mapping Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(seed_ece_curriculum())
