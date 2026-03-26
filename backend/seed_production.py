import os, asyncio, sys
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def run_seeders():
    print("=== SyllabusMapper Master Seeder ===")
    print("This script will populate your database with:")
    print("1. Job Roles & Skill Nodes (L0-L5)")
    print("2. ECE Curriculum & Courses")
    print("3. AI-generated Skill Mappings")
    
    # Check for required environment variables
    required = ['SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
    missing = [r for r in required if not os.environ.get(r)]
    
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Please ensure your .env file has these set before running.")
        return

    # Import the seeders
    try:
        from data.seed_l0l5 import seed as seed_skills
        from data.seed_ece_curriculum import seed_ece_curriculum
        from data.seed_domain_mockup import seed_domains
    except ImportError as e:
        print(f"ERROR: Could not import seeding scripts: {e}")
        return

    print("\n--- Phase 1: Seeding Job Roles & Skill Nodes ---")
    await seed_skills()
    
    print("\n--- Phase 2: Seeding Additional Domains ---")
    await seed_domains()
    
    print("\n--- Phase 3: Seeding ECE Curriculum & Mappings ---")
    await seed_ece_curriculum()
    
    print("\n=== All Seeding Completed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(run_seeders())
