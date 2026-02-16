
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import generate_response

router = APIRouter(prefix="/llm", tags=["llm"])


class PromptRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: PromptRequest):
    response = await generate_response(request.message)
    return {"response": response}
