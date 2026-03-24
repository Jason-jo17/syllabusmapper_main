import os, httpx, uuid, io, time, asyncio
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, UploadFile, BackgroundTasks
from pydantic import BaseModel
import google.generativeai as genai
from services.mapper import map_syllabus_cos

router = APIRouter()

def get_config():
    from dotenv import load_dotenv
    load_dotenv()
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_KEY', '')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    return url, key, headers

class URLIngest(BaseModel):
    url: str
    college_id: str
    stream: str
    regulation: str

async def get_embeddings_batched(texts: List[str]):
    if not texts: return []
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    embeddings = []
    # Gemini embedding allows batching but let's just do it in chunks of 50 to avoid any limits
    for i in range(0, len(texts), 50):
        batch = texts[i:i+50]
        try:
             result = genai.embed_content(model="models/gemini-embedding-001", content=batch)
             for item in result['embeddings']:
                 emb = item
                 padded = emb[:1024] if len(emb) >= 1024 else emb + [0.0]*(1024-len(emb))
                 embeddings.append(padded)
        except Exception as e:
             print(f"Embedding error: {e}")
             # placeholder for failure
             embeddings.extend([[0.0]*1024] * len(batch))
        await asyncio.sleep(1.0) # Respect rate limits
    return embeddings

async def process_and_map_csv_async(syl_id: str, df: pd.DataFrame):
     url, key, h = get_config()
     if not url: return
     
     async with httpx.AsyncClient(headers=h, timeout=60.0) as client:
         # Clean columns
         df.columns = [str(c).strip().strip("'").strip('"') for c in df.columns]
         
         # 1. Identify Columns
         code_col = next((c for c in df.columns if 'Course code' in c), 'Course code')
         name_col = next((c for c in df.columns if 'Course name' in c or 'Course' == c), 'Course name')
         co_col = next((c for c in df.columns if 'CO' == c or 'Outcome' in c), 'CO')
         desc_col = next((c for c in df.columns if 'CO Description' in c or 'Outcome Description' in c), 'CO Description')
         
         print(f"Mapping columns: {code_col}, {name_col}, {co_col}, {desc_col}")
         
         if code_col not in df.columns:
              print(f"Missing Course code column in {list(df.columns)}")
              await client.patch(f"{url}/rest/v1/syllabi?id=eq.{syl_id}", json={'ingestion_status': 'failed'})
              return

         # 2. Sync Courses
         unique_courses = df[[code_col, name_col]].drop_duplicates().dropna(subset=[code_col])
         for _, row in unique_courses.iterrows():
             code = str(row[code_col]).strip()
             name = str(row[name_col]).strip()
             await client.post(f"{url}/rest/v1/courses", headers={"Prefer": "resolution=merge-duplicates"}, json={
                 'id': f"{syl_id}_{code}", 'syllabus_id': syl_id, 'course_code': code, 'title': name, 'semester': 1, 'credits': 3
             })

         # 3. Sync COs (Batched Embeddings)
         co_data = df[[code_col, co_col, desc_col]].dropna().to_dict('records')
         descs = [str(r[desc_col]) for r in co_data]
         
         print(f"Generating embeddings for {len(descs)} COs...")
         all_embs = await get_embeddings_batched(descs)
         
         print(f"Upserting {len(co_data)} COs...")
         for i, r in enumerate(co_data):
             code = str(r[code_col]).strip()
             co_code = str(r[co_col]).strip()
             desc = descs[i]
             emb = all_embs[i]
             
             await client.post(f"{url}/rest/v1/course_outcomes", headers={"Prefer": "resolution=merge-duplicates"}, json={
                 'id': f"{syl_id}_{code}_{co_code}", 'course_id': f"{syl_id}_{code}",
                 'co_code': co_code, 'description': desc, 'embedding': emb
             })
         
         await client.patch(f"{url}/rest/v1/syllabi?id=eq.{syl_id}", json={'ingestion_status': 'completed'})
         
         print(f"Triggering auto-mapping for {syl_id}...")
         try:
             await map_syllabus_cos(syl_id)
         except Exception as e:
             print(f"Mapping failed: {e}")

@router.post("/csv")
async def upload_csv(file: UploadFile, bg: BackgroundTasks):
    url, key, h = get_config()
    if not url: return {"error": "Config missing"}
    
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    syl_id = str(uuid.uuid4())
    
    # Init syllabus record
    async with httpx.AsyncClient(headers=h) as client:
        await client.post(f"{url}/rest/v1/syllabi", json={
            'id': syl_id, 'college_id': 'default_college', 'stream': 'CSV Upload', 'regulation': '2024',
            'title': file.filename, 'source_type': 'csv', 'ingestion_status': 'processing'
        })
    
    bg.add_task(process_and_map_csv_async, syl_id, df)
    return {"id": syl_id, "status": "processing"}
