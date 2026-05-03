from fastapi import APIRouter, HTTPException

from app.agents.KnowledgeAgent import KnowledgeAgentInstance
from app.api.schemas.Chat import ChatRequest, ChatResponse

Router = APIRouter(prefix="/chat", tags=["chat"])

@Router.post("/message", response_model=ChatResponse)
async def SendMessage(Body: ChatRequest) -> ChatResponse:
    try:
        History = [{"role": Msg.role, "content": Msg.content} for Msg in Body.history]
        Result = await KnowledgeAgentInstance.Process(Body.message, History)
        return ChatResponse(
            answer=Result.Answer,
            category=Result.Category,
            answered_by_agent=Result.AnsweredByAgent,
        )
    except Exception as Error:
        raise HTTPException(status_code=500, detail=str(Error))