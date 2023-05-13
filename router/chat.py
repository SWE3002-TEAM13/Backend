from fastapi import APIRouter, Depends, WebSocket
from auth.oauth2 import get_current_user
from db.database import get_db
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

    return db_chat.getChatRoomList(current_user.id, db)


@router.get("/chatroom/{chatroom_id}")
def getChatRoomInfo(chatroom_id: int, db: Session = Depends(get_db), current_user: UserInfoBase = Depends(get_current_user)):

    return db_chat.getChatRoomMessage(chatroom_id, current_user.id, db)

chat_client = []

@router.websocket("/ws/{chatroom_id}")
async def sendChatMessage(websocket: WebSocket, chatroom_id: int, db: Session = Depends(get_db),
                         current_user: UserInfoBase = Depends(get_current_user)):
    
    valid = db_chat.checkChatRoom(chatroom_id, current_user.id, db)
    
    if valid != "valid": return "Non Valid!"
    
    await websocket.accept()
    chat_client.append(websocket)
    while True:
        message = await websocket.receive_text()
        if not message: continue
        db_chat.createChatMessage(chatroom_id, current_user.id, message, db)

        for client in chat_client:
            await client.send_text(message)