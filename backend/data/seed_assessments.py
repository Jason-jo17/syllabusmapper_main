import pandas as pd
import asyncio, os, json, uuid, sys, math
from typing import Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client, ClientOptions

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')
options = ClientOptions(postgrest_client_timeout=120)
sb = create_client(url, key, options=options)

def sanitize_value(val: Any) -> Any:
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)): return None
    return str(val).strip()

async def seed_assessments():
    paths = ['D:/Downloads2/skill_assessment_questions_complete.csv', 'D:/Downloads2/skill_assessment_questions_v4 (2).csv']
    
    print("Clearing existing assessments...")
    sb.table('skill_assessments').delete().neq('domain', '').execute()

    for path in paths:
        if not os.path.exists(path): continue
        print(f"Processing {path}...")
        df = pd.read_csv(path)
        for i, row in df.iterrows():
            try:
                domain = sanitize_value(row.get('domain'))
                ks = sanitize_value(row.get('knowledge_set'))
                sk = sanitize_value(row.get('skill_knowledge'))
                if not domain or not sk: continue
                
                # Direct Lookup per row
                sk_clean = sk.split(' - BL')[0].lower().strip()
                # Use ilike or exact match on skill_description starting with the clean text
                res = sb.table('skill_nodes').select('id').eq('domain', domain).ilike('skill_description', f"{sk_clean}%").limit(1).execute()
                
                if not res.data:
                    # Try fallback without domain if needed, but risky. Let's stick to domain+skill.
                    continue
                node_id = res.data[0]['id']
                
                mcqs = []
                for j in range(1, 4):
                    q = sanitize_value(row.get(f'mcq{j}_question'))
                    if q:
                        mcqs.append({
                            "question": q, "bl": sanitize_value(row.get(f'mcj{j}_bl')), # Fixing typo mcj -> mcq if any
                            "options": [
                                {"text": sanitize_value(row.get(f'mcq{j}_optA_text')), "weight": sanitize_value(row.get(f'mcq{j}_optA_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{j}_optB_text')), "weight": sanitize_value(row.get(f'mcq{j}_optB_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{j}_optC_text')), "weight": sanitize_value(row.get(f'mcq{j}_optC_weight'))},
                                {"text": sanitize_value(row.get(f'mcq{j}_optD_text')), "weight": sanitize_value(row.get(f'mcq{j}_optD_weight'))}
                            ],
                            "correct_answer": sanitize_value(row.get(f'mcq{j}_correct_answer'))
                        })
                
                subjective_tasks = []
                for j in range(1, 3):
                    q = sanitize_value(row.get(f'sub{j}_question'))
                    if q:
                        rubrics = []
                        for r in range(1, 3):
                            elem = sanitize_value(row.get(f'sub{j}_rub{r}_element'))
                            if elem:
                                rubrics.append({
                                    "element": elem, "description": sanitize_value(row.get(f'sub{j}_rub{r}_description')),
                                    "score5_expert": sanitize_value(row.get(f'sub{j}_rub{r}_score5_expert')),
                                    "score3_proficient": sanitize_value(row.get(f'sub{j}_rub{r}_score3_proficient')),
                                    "score1_emerging": sanitize_value(row.get(f'sub{j}_rub{j}_score1_emerging'))
                                })
                        subjective_tasks.append({"question": q, "hint": sanitize_value(row.get(f'sub{j}_hint')), "rubrics": rubrics})
                
                record = {
                    "skill_node_id": node_id, "domain": domain, "knowledge_set": ks,
                    "skill_knowledge": sk, "mcqs": mcqs, "subjective_tasks": subjective_tasks
                }
                sb.table('skill_assessments').insert(record).execute()
                print(f"  [+] Ingested row {i+1} ({sk[:30]}...)")
                await asyncio.sleep(0.05)
            except Exception as e:
                print(f"  [-] Error at row {i+1}: {e}")

    print("Assessment Seeding Finalized Successfully.")

if __name__ == "__main__":
    asyncio.run(seed_assessments())
