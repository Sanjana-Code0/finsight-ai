from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    role: str = Field(..., example="user") # 'user' or 'assistant'
    content: str = Field(..., example="Why was this specific fund recommended to me?")
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-123",
                "session_id": "session-456",
                "role": "user",
                "content": "Why was this specific fund recommended to me?",
                "created_at": "2023-10-27T10:10:00Z"
            }
        }

class ChatSession(BaseModel):
    id: str
    user_id: str
    assessment_id: Optional[str] = None
    created_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "session-456",
                "user_id": "987e6543-e21b-34d3-a456-426614174111",
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2023-10-27T10:05:00Z",
                "messages": []
            }
        }

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, example="session-456")
    assessment_id: Optional[str] = Field(None, example="123e4567-e89b-12d3-a456-426614174000")
    message: str = Field(..., example="Why was this specific fund recommended to me?")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-456",
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Why was this specific fund recommended to me?"
            }
        }

class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-456",
                "message": {
                    "id": "msg-124",
                    "session_id": "session-456",
                    "role": "assistant",
                    "content": "This fund is recommended because it matches your long-term horizon and high risk tolerance.",
                    "created_at": "2023-10-27T10:10:05Z"
                }
            }
        }
