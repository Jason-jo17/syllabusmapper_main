# backend/data/seed_l0l5.py
# Run once to populate skill_nodes + job_roles from XLSX files
import pandas as pd, asyncio, os, json, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv; load_dotenv()
from supabase import create_client
from services.embedder import batch_embed

url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_KEY', '')
print(f"Connecting to: {url}")
sb = create_client(url, key)

ROLE_FILES = {
    'Embedded Electronics Engineer': ('ECE_L0L5_VTU_CO_v2.xlsx', 'ECE L0-L5 + CO Map'),
    'Software Developer': ('SW_Dev_L0_L5_Concepts_Skills.xlsx', 'L0-L5 Full Breakdown'),
    'Data Engineer': ('Data_Engineer_L0_L5_Breakdown.xlsx', 'DE L0-L5 Full Breakdown'),
    'Full Stack DataDev': ('FullStack_DataDev_L0_L5_Breakdown.xlsx', 'FSDD L0-L5 Full Breakdown'),
}

COL_MAP = {
    'Embedded Electronics Engineer': {
        'level':'Level','ks':'Knowledge Set','concept':'Concept (What to KNOW)',
        'skill':'Skill Knowledge (What to DO) -BL','bl':'BL','task':'Task Type',
        'tools':'Tools','year':'Year','role':'Role Proximity','tag':'Common Tag',
        'domain':'Domain','category':'Category',
        'co1_text':'ECE CO — Primary\n(Course Outcome Text)',
        'co1_course':'Primary\nCourse Title','co1_year':'Primary\nYear','co1_sem':'Primary\nSem',
        'co2_text':'ECE CO — Secondary\n(Course Outcome Text)',
        'co2_course':'Secondary\nCourse Title','co2_year':'Secondary\nYear','co2_sem':'Secondary\nSem',
        'co3_text':'ECE CO — Tertiary\n(Course Outcome Text)',
        'co3_course':'Tertiary\nCourse Title','co3_year':'Tertiary\nYear','co3_sem':'Tertiary\nSem',
    },
}

async def seed():
    # We handle cleanup per-role inside the loop to avoid foreign key violations
    for role_name, (fname, sheet) in ROLE_FILES.items():
        fpath = os.path.join('data', fname)
        if not os.path.exists(fpath):
            print(f"Skipping {role_name}, file not found: {fpath}")
            continue
            
        print(f"Processing role: {role_name}")
        existing = sb.table('job_roles').select('id').eq('role_name', role_name).execute()
        
        if existing.data:
            role_id = existing.data[0]['id']
            # Clear existing nodes for THIS role to allow fresh seed
            print(f"Clearing existing nodes for {role_name} to re-seed...")
            sb.table('skill_nodes').delete().eq('job_role_id', role_id).execute()
        else:
            print(f"Creating new role: {role_name}")
            role_row = sb.table('job_roles').insert({
                'role_name': role_name, 'domain': 'Engineering'
            }).execute()
            role_id = role_row.data[0]['id']
            
        df = pd.read_excel(fpath, sheet_name=sheet)
        rows = df.to_dict('records')
        print(f"Read {len(rows)} rows from {fname}")
        def s(r,k): v=r.get(k,''); return '' if pd.isna(v) else str(v).strip()
        
        print(f"Gathering texts for {len(rows)} nodes...")
        texts = [f"Level:{s(r,'Level')}\nKS:{s(r,'Knowledge Set')}\nConcept:{s(r,'Concept (What to KNOW)')}\nSkill:{s(r,'Skill Knowledge (What to DO) -BL')}"[:2000] for r in rows]
        
        print(f"Embedding {len(texts)} texts...")
        embeddings = await batch_embed(texts)
        if embeddings and len(embeddings) > 0:
            print(f"DEBUG: First embedding sample: {embeddings[0][:5]}...")
        else:
            print("WARNING: No embeddings returned from batch_embed!")
            continue # Skip this role if we got nothing
        
        inserts = []
        for r, emb in zip(rows, embeddings):
            lvl = s(r,'Level')
            # Check if lvl is valid
            if not lvl: continue
            
            node = {
                'job_role_id': role_id,
                'level': lvl,
                'level_num': int(lvl[1]) if lvl and len(lvl) > 1 and lvl[1].isdigit() else 0,
                'common_tag': s(r,'Common Tag'),
                'domain': s(r,'Domain'),
                'category': s(r,'Category'),
                'knowledge_set': s(r,'Knowledge Set'),
                'concept': s(r,'Concept (What to KNOW)'),
                'skill_description': s(r,'Skill Knowledge (What to DO) -BL'),
                'bloom_level': int(r.get('BL',0)) if not pd.isna(r.get('BL',0)) else 0,
                'task_type': s(r,'Task Type'),
                'tools': s(r,'Tools'),
                'year_label': s(r,'Year'),
                'role_proximity': s(r,'Role Proximity'),
                'embedding': emb,
            }
            if role_name == 'Embedded Electronics Engineer':
                cm = COL_MAP[role_name]
                node.update({
                    'co_primary_text': s(r,cm['co1_text']),
                    'co_primary_course': s(r,cm['co1_course']),
                    'co_primary_year': s(r,cm['co1_year']),
                    'co_primary_sem': s(r,cm['co1_sem']),
                    'co_secondary_text': s(r,cm['co2_text']),
                    'co_secondary_course': s(r,cm['co2_course']),
                    'co_secondary_year': s(r,cm['co2_year']),
                    'co_secondary_sem': s(r,cm['co2_sem']),
                    'co_tertiary_text': s(r,cm['co3_text']),
                    'co_tertiary_course': s(r,cm['co3_course']),
                    'co_tertiary_year': s(r,cm['co3_year']),
                    'co_tertiary_sem': s(r,cm['co3_sem']),
                })
            inserts.append(node)
        
        print(f"Constructed {len(inserts)} inserts for {role_name}")
        # Chunked inserts for reliability
        chunk_size = 50
        print(f"Inserting nodes in chunks of {chunk_size}...")
        for i in range(0, len(inserts), chunk_size):
            chunk = inserts[i:i+chunk_size]
            try:
                res = sb.table('skill_nodes').insert(chunk).execute()
                if res.data:
                    print(f"Inserted chunk {i//chunk_size + 1}/{(len(inserts)-1)//chunk_size + 1}")
                else:
                    print(f"FAILED chunk {i//chunk_size + 1}: No data returned")
            except Exception as e:
                print(f"FAILED chunk {i//chunk_size + 1}: {e}")
                
        print(f"Completed seeding {len(inserts)} nodes for {role_name}")


if __name__ == '__main__':
    asyncio.run(seed())
