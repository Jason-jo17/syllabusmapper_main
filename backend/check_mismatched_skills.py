import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
sb: Client = create_client(url, key)

async def check_mappings():
    # Find LICs Lab course
    res = sb.table('courses').select('*').ilike('course_name', '%LIC%').execute()
    if not res.data:
        print("No LICs Lab course found")
        return
    
    for course in res.data:
        print(f"\nCourse: {course['course_name']} ({course['id']})")
        
        # Get outcomes
        cos = sb.table('course_outcomes').select('*').eq('course_id', course['id']).execute()
        print(f"Outcomes: {len(cos.data)}")
        
        for co in cos.data:
            print(f"  CO: {co['co_code']} - {co['description'][:50]}...")
            # Get mappings
            mappings = sb.table('co_skill_mappings').select('*, skill_nodes(*)').eq('course_outcome_id', co['id']).execute()
            if not mappings.data:
                print("    No mappings found for this CO")
                continue
            
            print(f"    Mappings for this CO: {len(mappings.data)}")
            for m in mappings.data:
                skill = m.get('skill_nodes')
                if skill:
                    print(f"      -> Skill: {skill['skill_name']} (L{skill.get('level', 'N/A')})")
                else:
                    print(f"      -> Skill ID: {m['skill_node_id']} (Node not found)")

if __name__ == "__main__":
    asyncio.run(check_mappings())
