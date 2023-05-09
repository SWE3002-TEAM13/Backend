from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from auth.oauth2 import get_current_user
from db.database import get_db

from db.models import ChatMessage, ChatRoom, Post
from sqlalchemy.orm.session import Session
from db import db_chat
from schemas import UserInfoBase

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/{user_id}")
def newChatRoom(user_id: int, db: Session = Depends(get_db),
                   current_user: UserInfoBase = Depends(get_current_user)):
    
    return db_chat.createChatRoom(user_id, current_user.id, db)


@router.get("")
def getChatRoom(current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):

    return db_chat.getChatRoom(current_user.id, db)


@router.get("/chatroom/{id}")
def getChatRoomInfo(id: int, db: Session = Depends(get_db), current_user: UserInfoBase = Depends(get_current_user)):

    return db_chat.getChatRoomMessage(id, db)

@router.websocket("/ws/{room_id}")
async def chat_room(websocket: WebSocket, room_id: int, db: Session = Depends(get_db),
                    current_user: UserInfoBase = Depends(get_current_user)):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        db_chat.createChatMessage(room_id, current_user.id, message, db)

        # process the message and send it back to the user
        response = f"{current_user.id}: {message}"
        await websocket.send_text(response)