import asyncio, os, sys
# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from dotenv import load_dotenv
load_dotenv('backend/.env')
from backend.services.embedder import batch_embed

async def main():
    print(f"Testing Gemini Embedding with model: text-embedding-004...")
    r = await batch_embed(['Test skills description'])
    if r and r[0]:
        print(f"Result length: {len(r[0])}")
        non_zero = any(x != 0 for x in r[0])
        print(f"Non-zero elements: {non_zero}")
        if non_zero:
            print(f"Sample: {r[0][:5]}...")
    else:
        print("Result is empty or None")

if __name__ == "__main__":
    asyncio.run(main())
