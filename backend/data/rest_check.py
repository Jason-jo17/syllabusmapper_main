import os, httpx
from dotenv import load_dotenv

def check():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    r = httpx.get(f"{url}/rest/v1/courses?select=*&limit=1", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")

if __name__ == "__main__":
    check()
