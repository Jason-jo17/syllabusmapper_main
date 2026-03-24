import google.generativeai as genai
import os
import time

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

async def batch_embed(texts):
    if not texts:
        return []
    
    # Gemini supports batching by passing the list of strings
    # But to be safe with rate limits/payload size, we'll do batches of 50
    all_embeddings = []
    batch_size = 50
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Embedding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch)} texts)...")
        
        success = False
        for attempt in range(5): # Up to 5 retries
            try:
                model_name = "models/gemini-embedding-001"
                
                if hasattr(genai, 'embed_content'):
                    result = genai.embed_content(
                        model=model_name,
                        content=batch,
                        task_type="semantic_similarity"
                    )
                else:
                    result = genai.embed_contents(
                        model=model_name,
                        contents=[{'content': t} for t in batch]
                    )



                
                batch_embs = result.get('embedding', []) if hasattr(result, 'get') else getattr(result, 'embeddings', [])
                for emb in batch_embs:
                    if len(emb) >= 1024:
                        padded = emb[:1024]
                    else:
                        padded = emb + [0.0] * (1024 - len(emb))
                    all_embeddings.append(padded)
                
                success = True
                time.sleep(10.0) # Normal delay
                break
            except Exception as e:
                print(f"Batch embedding attempt {attempt+1} error: {e}")
                if "429" in str(e):
                    wait_time = 60 * (attempt + 1)
                    print(f"Quota exhausted, sleeping {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(5.0)
        
        if not success:
            print(f"CRITICAL: Failed to embed batch after 5 attempts. Filling with zeros.")
            for _ in batch:
                all_embeddings.append([0.0]*1024)


            
    return all_embeddings
