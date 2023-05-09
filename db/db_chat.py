import statistics
from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from sqlalchemy import or_

from db.models import ChatMessage, ChatRoom

def getChatRoomList(id: int, db: Session):
    chatroomlist = db.query(ChatRoom).filter(or_(ChatRoom.receiver_id == id, ChatRoom.sender_id == id))

    return chatroomlist

def getChatRoomMessage(id: int, user_id : int, db: Session):

    chatroom = db.query(ChatRoom).filter(ChatRoom.id == id, or_(ChatRoom.receiver_id == user_id, ChatRoom.sender_id == user_id)).all()

    if not chatroom:
         raise HTTPException(status_code=statistics.HTTP_403_FORBIDDEN,
                            detail=f"No Access Authority")       

    chatmessages = db.query(ChatMessage).filter(ChatMessage.chatroom_id == id).order_by(ChatMessage.created_at.desc()).all()

    return chatmessages

def createChatRoom(receiver: int, sender: int, db: Session):
    chatroom1 = db.query(ChatRoom).filter(ChatRoom.receiver_id == receiver, ChatRoom.sender_id == sender).first()
    chatroom2 = db.query(ChatRoom).filter(ChatRoom.receiver_id == sender, ChatRoom.sender_id == receiver).first()

    if chatroom1 or chatroom2:
        raise HTTPException(status_code=statistics.HTTP_403_FORBIDDEN,
                            detail=f"ChatRoom Already Exist!")
    new_chatroom = ChatRoom(receiver = receiver, sender = sender)
    db.add(new_chatroom)
    db.commit()
    db.refresh(new_chatroom)


def createChatMessage(chatroom_id : int, sender_id : int, message : str, db : Session):

    chatroom = db.query(ChatRoom).filter(ChatRoom.id == chatroom_id).first()

    if not chatroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found")

    chat_message = ChatMessage(chatroom_id=chatroom_id, sender_id=sender_id, message=message)
    db.add(chat_message)
    db.commit()
