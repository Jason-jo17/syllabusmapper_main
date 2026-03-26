import traceback
import logging
import os
from dotenv import load_dotenv

# Load env before any local imports that might use them
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import syllabi, skills, courses, ingest, gap, colleges, chat, events, assessments, assignments
# Setup logging to a file
logging.basicConfig(
    filename='server_error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s'
)

print("Creating app...")
app = FastAPI()
print("App created.")

print("Adding middleware...")
cors_origins = os.environ.get(
    "CORS_ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000,https://syllabusmapper-main.vercel.app,https://syllabusmappermain-production.up.railway.app"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("Middleware added.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Error: {str(exc)}\n{traceback.format_exc()}"
    logging.error(error_msg)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)}
    )

print("Including routers...")
app.include_router(syllabi.router, prefix="/api/syllabi", tags=["syllabi"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(gap.router, prefix="/api/gap", tags=["gap"])
app.include_router(colleges.router, prefix="/api/colleges", tags=["colleges"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["assessments"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["assignments"])
print("Routers included.")

@app.get("/")
async def root():
    return {"message": "Syllabus Mapper API"}
