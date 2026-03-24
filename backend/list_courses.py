import httpx
try:
    r = httpx.get('http://127.0.0.1:8000/api/courses/')
    if r.status_code == 200:
        courses = r.json()
        print(f"Total Courses: {len(courses)}")
        for c in sorted(courses, key=lambda x: str(x.get("course_code"))):
            print(f"{c.get('course_code')}: {c.get('course_title')}")
    else:
        print(f"API Error {r.status_code}: {r.text}")
except Exception as e:
    print(f"Error: {e}")
