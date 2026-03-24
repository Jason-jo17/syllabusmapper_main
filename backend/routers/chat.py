from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatReq(BaseModel):
    message: str
    context: dict = {}

@router.post("/")
def chat(req: ChatReq):
    return {"message": "Chat response via Claude... (implemented soon)"}
