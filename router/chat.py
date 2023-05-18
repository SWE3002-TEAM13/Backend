import json
from db.models import User
from fastapi import APIRouter, Depends, WebSocket, HTTPException, status, WebSocketDisconnect
from auth.oauth2 import get_current_user, verify_token
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

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
manager = ConnectionManager()
            
@router.websocket("/ws/{chatroom_id}")
async def sendChatMessage(websocket: WebSocket, chatroom_id: int, token: str | None, db: Session = Depends(get_db)):
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Not Auth User")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = verify_token(token, credentials_exception, db)
    
    valid = db_chat.checkChatRoom(chatroom_id, user.id, db)
    
    if valid != "valid": return "Non Valid!"
    
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            if not message: continue
            message = db_chat.createChatMessage(chatroom_id, user.id, message, db)
            user = db.query(User).filter(User.id == message.sender_id).first()
            sender_profile = {"nickname": user.nickname, "thumbnail": user.thumbnail}
            chat = {"id" : message.id, "chatroom_id" : message.chatroom_id, "sender_id" : message.sender_id, "sender_profile" : sender_profile, "message" : message.message, "created_at" : message.created_at}
            await manager.broadcast(json.dumps(chat))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")