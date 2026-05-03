from pydantic import BaseModel, Field, field_validator

class HistoryMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)

    @field_validator("message")
    @classmethod
    def ValidateMessage(cls, Value: str) -> str:
        try:
            if not Value.strip():
                raise ValueError("Message must not be blank.")
            return Value.strip()
        except Exception as Error:
            raise Error

class ChatResponse(BaseModel):
    answer: str
    category: str
    answered_by_agent: bool