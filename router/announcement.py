from sqlalchemy.orm import Session
from auth.oauth2 import get_current_user
from db.database import get_db
from fastapi import APIRouter, Depends, Form
from db.models import Announcement
from schemas import UserInfoBase, AnnounceDisplay, AnnounceUpdate
from db import db_announcement
from datetime import datetime


router = APIRouter(
    prefix="/announcement",
    tags=["announcement"]
)

@router.get('/')
def get_announcement_list(db: Session = Depends(get_db)):
    announcement = db.query(Announcement).filter().all()
    return announcement

@router.get('/{id}')
def getAnnounceInfo(id: int, db: Session = Depends(get_db)):
    announceinfo = db.query(Announcement).filter(Announcement.id == id).first()
    return announceinfo


@router.post('/')
async def register(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    announce = AnnounceDisplay(title=title, content=content, created_at=datetime.now(), updated_at=datetime.now())
    return db_announcement.register_announce(announce, db)

@router.put('/{id}')
def updateAnnounce(id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    announce = AnnounceUpdate(title=title, content=content, updated_at=datetime.now())
    return db_announcement.update_announce(id, announce,  db)


@router.delete('/{id}')
def deleteAnnounce(id: int, db: Session = Depends(get_db)):
    return db_announcement.delete_announce(id, db)