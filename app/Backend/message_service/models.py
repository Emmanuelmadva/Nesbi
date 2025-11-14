from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from app.Backend.auth_service.models import User

# ------------------------------------------------
#                 CONVERSATION
# ------------------------------------------------
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"))
    user2_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    participants = relationship("ConversationUser", back_populates="conversation", cascade="all, delete-orphan")


# ------------------------------------------------
#                     MESSAGE
# ------------------------------------------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    # Relations
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship(User)  # utiliser la classe directement


# ------------------------------------------------
#         TABLE PIVOT (Conversation ↔ User)
# ------------------------------------------------
class ConversationUser(Base):
    __tablename__ = "conversation_user"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    deleted = Column(Boolean, default=False)
    last_read_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)

    conversation = relationship("Conversation", back_populates="participants")
    user = relationship(User)
