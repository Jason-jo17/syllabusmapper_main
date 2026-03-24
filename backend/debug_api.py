import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load env before importing routers
load_dotenv()

from routers import skills, syllabi

async def test_skills():
    print("\n--- Testing get_skills ---")
    try:
        r = await skills.get_skills(role="Embedded Electronics")
        print(f"Skills Count: {len(r)}")
    except Exception as e:
        import traceback
        traceback.print_exc()

async def test_syllabi():
    print("\n--- Testing get_syllabus_courses ---")
    syl_id = "ece00000-0000-0000-0000-000000000000"
    try:
        r = await syllabi.get_syllabus_courses(syl_id)
        print(f"Courses Count: {len(r)}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_skills())
    asyncio.run(test_syllabi())
