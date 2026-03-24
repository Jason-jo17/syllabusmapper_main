import os, httpx, json
from dotenv import load_dotenv

def export_db_state():
    load_dotenv()
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    with httpx.Client(headers=headers, timeout=60.0) as client:
        r1 = client.get(f"{url}/rest/v1/courses?select=*")
        r2 = client.get(f"{url}/rest/v1/skill_nodes?select=*")
        r3 = client.get(f"{url}/rest/v1/course_outcomes?select=*")
        
        state = {
            'courses': r1.json() if r1.status_code == 200 else [],
            'skills': r2.json() if r2.status_code == 200 else [],
            'cos': r3.json() if r3.status_code == 200 else []
        }
        
        with open('db_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    print("Database state exported to db_state.json")

if __name__ == "__main__":
    export_db_state()
