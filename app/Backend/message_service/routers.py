from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Conversation, Message, ConversationUser
from schemas import ConversationCreate, ConversationRead, MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["Messages"])

# -----------------------------
# Conversations
# -----------------------------
@router.post("/conversations/", response_model=ConversationRead)
def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db)):

    from app.Backend.auth_service.models import User

    user1 = db.query(User).filter(User.id == conv.user1_id).first()
    user2 = db.query(User).filter(User.id == conv.user2_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="Un ou plusieurs utilisateurs n'existent pas")

    existing = db.query(Conversation).filter(
        ((Conversation.user1_id == conv.user1_id) & (Conversation.user2_id == conv.user2_id)) |
        ((Conversation.user1_id == conv.user2_id) & (Conversation.user2_id == conv.user1_id))
    ).first()

    if existing:
        return existing

    new_conv = Conversation(user1_id=conv.user1_id, user2_id=conv.user2_id)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    db.add(ConversationUser(conversation_id=new_conv.id, user_id=conv.user1_id))
    db.add(ConversationUser(conversation_id=new_conv.id, user_id=conv.user2_id))
    db.commit()

    return new_conv


@router.get("/conversations/{user_id}", response_model=List[ConversationRead])
def list_user_conversations(user_id: int, db: Session = Depends(get_db)):
    return db.query(Conversation).filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
    ).all()


# -----------------------------
# Messages
# -----------------------------
@router.post("/", response_model=MessageRead)
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    from app.Backend.auth_service.models import User

    conv = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation non trouver")

    sender = db.query(User).filter(User.id == msg.sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="L'envoyeur n'existe pas")

    if msg.sender_id not in [conv.user1_id, conv.user2_id]:
        raise HTTPException(status_code=403, detail="utilisateur absent dans la conversation")

    message = Message(
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        content=msg.content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/{conv_id}", response_model=List[MessageRead])
def get_messages(conv_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.timestamp).all()


# -----------------------------
# Suppression locale
# -----------------------------
@router.delete("/conversations/{conv_id}/delete/{user_id}")
def delete_conversation_local(conv_id: int, user_id: int, db: Session = Depends(get_db)):

    from app.Backend.auth_service.models import User

    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    link = db.query(ConversationUser).filter(
        ConversationUser.conversation_id == conv_id,
        ConversationUser.user_id == user_id
    ).first()

    if not link:
        link = ConversationUser(
            conversation_id=conv_id,
            user_id=user_id,
            deleted=True
        )
        db.add(link)
    else:
        link.deleted = True

    db.commit()
    return {"message": "Conversation supprimée localement"}


# -----------------------------
# Restaurer la conversation
# -----------------------------
@router.post("/conversations/{conv_id}/restore/{user_id}")
def restore_conversation(conv_id: int, user_id: int, db: Session = Depends(get_db)):

    from app.Backend.auth_service.models import User

    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    link = db.query(ConversationUser).filter(
        ConversationUser.conversation_id == conv_id,
        ConversationUser.user_id == user_id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Conversation non trouvée pour cet utilisateur")

    link.deleted = False
    db.commit()
    return {"message": "Conversation restaurée"}


# -----------------------------
# Conversations visibles
# -----------------------------
@router.get("/conversations/visible/{user_id}", response_model=List[ConversationRead])
def list_visible_conversations(user_id: int, db: Session = Depends(get_db)):
    hidden_ids = db.query(ConversationUser.conversation_id).filter(
        ConversationUser.user_id == user_id,
        ConversationUser.deleted == True
    )

    conversations = db.query(Conversation).filter(
        ((Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)),
        ~Conversation.id.in_(hidden_ids)
    ).all()

    return conversations


# -----------------------------
# Marquer messages comme lus
# -----------------------------
@router.post("/{conv_id}/read/{user_id}")
def mark_as_read(conv_id: int, user_id: int, db: Session = Depends(get_db)):

    from app.Backend.auth_service.models import User
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    last_msg = db.query(Message).filter(
        Message.conversation_id == conv_id
    ).order_by(Message.id.desc()).first()

    if not last_msg:
        return {"message": "Aucun message dans cette conversation"}

    link = db.query(ConversationUser).filter(
        ConversationUser.conversation_id == conv_id,
        ConversationUser.user_id == user_id
    ).first()

    if not link:
        link = ConversationUser(
            conversation_id=conv_id,
            user_id=user_id,
            last_read_message_id=last_msg.id
        )
        db.add(link)
    else:
        link.last_read_message_id = last_msg.id

    db.commit()
    return {"message": "Messages marqués comme lus"}
