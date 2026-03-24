import httpx
import time

def test():
    start = time.time()
    try:
        r = httpx.get("http://localhost:8000/api/skills?role=Embedded Electronics Engineer", timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Time: {time.time() - start:.2f}s")
        if r.status_code == 200:
            data = r.json()
            print(f"Count: {len(data)}")
            if data:
                print(f"First item keys: {data[0].keys()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
