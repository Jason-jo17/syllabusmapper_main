import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

def test_insert():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    sb = create_client(url, key)
    
    # Get a real CO and Skill ID first
    co = sb.table('course_outcomes').select('id, course_id').limit(1).execute().data
    sk = sb.table('skill_nodes').select('id').limit(1).execute().data
    
    if not co or not sk:
        print("CO or Skill not found!")
        return
    
    mapping = {
        'id': str(uuid.uuid4()),
        'syllabus_id': 'ece00000-0000-0000-0000-000000000000',
        'course_id': co[0]['course_id'],
        'co_id': co[0]['id'],
        'skill_node_id': sk[0]['id'],
        'match_type': 'test',
        'similarity_score': 1.0
    }
    
    try:
        res = sb.table('co_skill_mappings').insert(mapping).execute()
        print(f"Success! {res.data}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_insert()
