from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: str

class MessageRead(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    timestamp: datetime
    read: bool

    class Config:
        orm_mode = True

class ConversationCreate(BaseModel):
    user1_id: int
    user2_id: int

class ConversationRead(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    messages: list[MessageRead] = []

    class Config:
        orm_mode = True
