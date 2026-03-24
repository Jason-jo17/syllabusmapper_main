import pandas as pd
import asyncio, os, json, uuid
from dotenv import load_dotenv; load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
from supabase import create_client

# Using the original Voyage AI / Gemini script embedder if available, otherwise mock it
try:
    from services.embedder import batch_embed
except ImportError:
    import google.generativeai as genai
    import time
    import google.generativeai as genai
    import time
    def batch_embed(texts):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        embeddings = []
        for t in texts:
            retries = 5
            backoff = 2
            while retries > 0:
                try:
                    result = genai.embed_content(model="models/gemini-embedding-001", content=t)
                    emb = result['embedding']
                    # Pad to 1024
                    if len(emb) >= 1024:
                        padded = emb[:1024]
                    else:
                        padded = emb + [0.0] * (1024 - len(emb))
                    embeddings.append(padded)
                    time.sleep(1.0) # Base rate limit
                    break
                except Exception as e:
                    if "429" in str(e):
                        print(f"Rate limited. Backing off {backoff}s...")
                        time.sleep(backoff)
                        backoff *= 2
                        retries -= 1
                    else:
                        print(f"Embedding error: {e}")
                        embeddings.append([0.0]*1024)
                        break
            if retries == 0:
                embeddings.append([0.0]*1024)
        return embeddings

sb = create_client(os.environ.get('SUPABASE_URL', ''), os.environ.get('SUPABASE_KEY', ''))

async def seed_domain_mockup():
    print("Reading Domain Mockup CSV...")
    csv_path = 'data/Event Mastersheet mockup - Domain, skillset L C (9).csv'
    
    # Check if the file exists from the working directory or adjust
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), 'Event Mastersheet mockup - Domain, skillset L C (9).csv')
        
    df = pd.read_csv(csv_path)

    role_name = "Domain Skills Mapping"
    print(f"Checking for existing role '{role_name}'...")
    role_resp = sb.table('job_roles').select('id').eq('role_name', role_name).execute()
    
    if role_resp.data:
         role_id = role_resp.data[0]['id']
         # Optional: clear existing
         sb.table('skill_nodes').delete().eq('job_role_id', role_id).execute()
    else:
         role_row = sb.table('job_roles').insert({
             'role_name': role_name, 'domain': 'Engineering'
         }).execute()
         role_id = role_row.data[0]['id']
         
    rows = df.to_dict('records')
    
    def s(r, k):
        v = r.get(k, '')
        return '' if pd.isna(v) else str(v).strip()

    texts_to_embed = []
    nodes = []
    
    # Process only rows that have a domain/skill
    for r in rows:
        domain = s(r, 'Domain')
        knowledge_set = s(r, 'knowlegde set')
        skill = s(r, 'skill knowledge')
        
        if not domain and not skill:
            continue
            
        texts_to_embed.append(f"Domain:{domain}\nKS:{knowledge_set}\nSkill:{skill}"[:2000])
        
        # Try to parse BL level from the skill string if it exists (e.g. "... - BL3")
        bloom_level = 0
        if "BL" in skill:
             part = skill.split("BL")[-1]
             if part and part[0].isdigit():
                 bloom_level = int(part[0])
                 
        node = {
            'job_role_id': role_id,
            'level': '', # Or map from engineering programs
            'level_num': 0,
            'common_tag': s(r, 'common tag ( try to make this based on subject)'),
            'domain': domain,
            'category': s(r, 'engineering programs '),
            'knowledge_set': knowledge_set,
            'concept': '',
            'skill_description': skill,
            'bloom_level': bloom_level,
            'co_primary_text': s(r, 'subject and co to map '),
        }
        nodes.append(node)
        
    print(f"Embedding {len(texts_to_embed)} skills...")
    # Process embeddings in batches if many
    batch_size = 10
    embeddings = []
    for i in range(0, len(texts_to_embed), batch_size):
        print(f"Batch {i}/{len(texts_to_embed)}")
        batch_texts = texts_to_embed[i:i+batch_size]
        batch_embs = await batch_embed(batch_texts) if asyncio.iscoroutinefunction(batch_embed) else batch_embed(batch_texts)
        embeddings.extend(batch_embs)
        
    for i, node in enumerate(nodes):
        node['embedding'] = embeddings[i]
        
    print(f"Inserting {len(nodes)} records to Supabase...")
    # Supabase maximum insert block size limits payload
    for i in range(0, len(nodes), 200):
        sb.table('skill_nodes').insert(nodes[i:i+200]).execute()
        
    print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_domain_mockup())
