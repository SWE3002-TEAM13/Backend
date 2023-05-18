from datetime import datetime
import statistics
from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from sqlalchemy import or_

from db.models import ChatMessage, ChatRoom, User

def getChatRoomList(id: int, db: Session):
    chatroomlist = db.query(ChatRoom).filter(or_(ChatRoom.receiver_id == id, ChatRoom.sender_id == id)).all()

    for chatroom in chatroomlist:
        
        chatroom.recent_message = ""
        chatroom.send_time = ""
        
        chatmessage = db.query(ChatMessage).filter(ChatMessage.chatroom_id == chatroom.id).order_by(ChatMessage.id.desc()).first()
        
        if chatmessage:
            chatroom.send_time = chatmessage.created_at
            chatroom.recent_message = chatmessage.message
            
        if chatroom.receiver_id != id:
            user = db.query(User).filter(User.id == chatroom.receiver_id).first()
            chatroom.profile = {"nickname" : user.nickname, "thumbnail" : user.thumbnail} 
        elif chatroom.sender_id != id:
            user = db.query(User).filter(User.id == chatroom.sender_id).first()
            chatroom.profile = {"nickname" : user.nickname, "thumbnail" : user.thumbnail} 
            
    return {"chatroom_info" : chatroomlist}

def getChatRoomMessage(chatroom_id: int, user_id : int, db: Session):

    chatroom = db.query(ChatRoom).filter(ChatRoom.id == chatroom_id, or_(ChatRoom.receiver_id == user_id, ChatRoom.sender_id == user_id)).first()

    if not chatroom:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No Access Authority")       

    chatmessages = db.query(ChatMessage).filter(ChatMessage.chatroom_id == chatroom_id).all()

    for message in chatmessages:
        
        user = db.query(User).filter(User.id == message.sender_id).first()
        message.sender_profile = {"nickname": user.nickname, "thumbnail": user.thumbnail}

    return chatmessages

def createChatRoom(receiver: int, sender: int, db: Session):
    recv_user = db.query(User).filter(User.id == receiver).first()
    send_user = db.query(User).filter(User.id == sender).first()

    if recv_user == send_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You can't talk yourself!")

    chatroom1 = db.query(ChatRoom).filter(ChatRoom.receiver_id == receiver, ChatRoom.sender_id == sender).first()
    chatroom2 = db.query(ChatRoom).filter(ChatRoom.receiver_id == sender, ChatRoom.sender_id == receiver).first()

    if not recv_user or not send_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Receiver User not Found!")       

    if chatroom1 or chatroom2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"ChatRoom Already Exist!")
    new_chatroom = ChatRoom(receiver_id = receiver, sender_id = sender)
    db.add(new_chatroom)
    db.commit()
    db.refresh(new_chatroom)

    return new_chatroom

def createChatMessage(chatroom_id : int, sender_id : int, message : str, db : Session):

    chatroom = db.query(ChatRoom).filter(ChatRoom.id == chatroom_id).first()

    if not chatroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found")

    chat_message = ChatMessage(chatroom_id=chatroom_id, sender_id=sender_id, message=message, created_at = datetime.now())
    db.add(chat_message)
    db.commit()
    
    return chat

def checkChatRoom(chatroom_id : int, user_id : int, db : Session):
    
    chatroom = db.query(ChatRoom).filter(ChatRoom.id == chatroom_id, or_(ChatRoom.receiver_id == user_id, ChatRoom.sender_id == user_id)).first()

    if not chatroom:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No Access Authority") 
         
    return "valid"