import google.generativeai as genai
import os, sys
# No venv needed for this simple check if we run it with the venv python
from dotenv import load_dotenv
load_dotenv('backend/.env')

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

print(f"GenAI version: {genai.__version__}")
try:
    print("Testing embed_content...")
    res = genai.embed_content(model="models/text-embedding-004", content="hello")
    print("Success! Embedding length:", len(res['embedding']))
except AttributeError as e:
    print(f"FAILED with AttributeError: {e}")
    print("Available methods:", [x for x in dir(genai) if 'embed' in x.lower()])
except Exception as e:
    print(f"FAILED with other error: {e}")
