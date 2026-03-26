import pandas as pd
import asyncio, os, json, uuid, sys, math
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')
sb = create_client(url, key)

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
        return None
    return str(val).strip()

async def seed_assessments():
    paths = [
        'D:/Downloads2/skill_assessment_questions_complete.csv',
        'D:/Downloads2/skill_assessment_questions_v4 (2).csv'
    ]
    
    # 1. Fetch all skill nodes for matching
    print("Fetching skill nodes for matching...")
    skill_nodes_res = sb.table('skill_nodes').select('id, domain, knowledge_set, skill_description').execute()
    skill_nodes = skill_nodes_res.data
    
    # Create a lookup map: (domain, cleaned_skill_description) -> id
    node_map = {}
    for sn in skill_nodes:
        # Strip Bloom Level suffix if present (e.g., " - BL3")
        sk_desc = str(sn['skill_description']).split(' - BL')[0].lower().strip()
        key_tuple = (
            str(sn['domain']).lower().strip(),
            sk_desc
        )
        node_map[key_tuple] = sn['id']

    all_inserts = []
    
    for path in paths:
        if not os.path.exists(path):
            print(f"WARNING: CSV not found at {path}")
            continue
            
        print(f"Processing {path}...")
        df = pd.read_csv(path)
        
        for _, row in df.iterrows():
            try:
                domain = sanitize_value(row.get('domain'))
                ks = sanitize_value(row.get('knowledge_set'))
                sk = sanitize_value(row.get('skill_knowledge'))
                
                # Try to find matching node
                node_id = None
                if domain and sk:
                    # Strip BL suffix if CSV somehow has it too
                    sk_clean = sk.split(' - BL')[0].lower().strip()
                    match_key = (domain.lower().strip(), sk_clean)
                    node_id = node_map.get(match_key)
                
                if not node_id:
                    print(f"  - Skipping (No node match): {sk}")
                    continue
                
                # Extract MCQs (1-3)
                mcqs = []
                for i in range(1, 4):
                    q = sanitize_value(row.get(f'mcq{i}_question'))
                    if q:
                        mcqs.append({
                            "question": q,
                            "bl": sanitize_value(row.get(f'mcq{i}_bl')),
                            "options": [
                                {"text": sanitize_value(row.get(f'mcq{i}_optA_text')), "weight": sanitize_value(row.get(f'mcq{i}_optA_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{i}_optB_text')), "weight": sanitize_value(row.get(f'mcq{i}_optB_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{i}_optC_text')), "weight": sanitize_value(row.get(f'mcq{i}_optC_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{i}_optD_text')), "weight": sanitize_value(row.get(f'mcq{i}_optD_weight'))}
                            ],
                            "correct_answer": sanitize_value(row.get(f'mcq{i}_correct_answer'))
                        })
                
                # Extract Subjective Tasks (1-2)
                subjective_tasks = []
                for i in range(1, 3):
                    q = sanitize_value(row.get(f'sub{i}_question'))
                    if q:
                        rubrics = []
                        for r in range(1, 3): # Most have 2 rubrics per sub-task
                            elem = sanitize_value(row.get(f'sub{i}_rub{r}_element'))
                            if elem:
                                rubrics.append({
                                    "element": elem,
                                    "description": sanitize_value(row.get(f'sub{i}_rub{r}_description')),
                                    "score5_expert": sanitize_value(row.get(f'sub{i}_rub{r}_score5_expert')),
                                    "score3_proficient": sanitize_value(row.get(f'sub{i}_rub{r}_score3_proficient')),
                                    "score1_emerging": sanitize_value(row.get(f'sub{i}_rub{r}_score1_emerging'))
                                })
                        subjective_tasks.append({
                            "question": q,
                            "hint": sanitize_value(row.get(f'sub{i}_hint')),
                            "rubrics": rubrics
                        })
                
                all_inserts.append({
                    "skill_node_id": node_id,
                    "domain": domain,
                    "knowledge_set": ks,
                    "skill_knowledge": sk,
                    "mcqs": mcqs,
                    "subjective_tasks": subjective_tasks
                })
            except Exception as e:
                print(f"Error processing row: {e}")

    if not all_inserts:
        print("No assessments found to insert.")
        return

    print(f"Clearing existing assessments...")
    sb.table('skill_assessments').delete().neq('domain', '').execute()

    print(f"Inserting {len(all_inserts)} assessments...")
    for i in range(0, len(all_inserts), 100):
        chunk = all_inserts[i:i+100]
        sb.table('skill_assessments').insert(chunk).execute()
        print(f"Inserted chunk {i//100 + 1}")

    print("Assessment Seeding Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(seed_assessments())
