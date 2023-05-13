from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from schemas import AnnounceDisplay, UserInfoBase
from db.models import Announcement, User
from fastapi import HTTPException, status


def register_announce(announce: AnnounceDisplay, db:Session):
    new_announce=Announcement(title = announce.title,
                  content = announce.content,
                  created_at = announce.created_at,
                  updated_at = announce.updated_at)
                  
    db.add(new_announce)
    db.commit()
    db.refresh(new_announce)
    return new_announce

def update_announce(id: int, announce: AnnounceDisplay, db:Session):
    db_announce = db.query(Announcement).filter(Announcement.id == id).first()
    if not db_announce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Announcement")
        
    db_announce.title = announce.title
    db_announce.content = announce.content
    db_announce.updated_at = announce.updated_at
    db.add(db_announce)
    db.commit()
    
def delete_announce(id: int, db: Session):
            
    delete_announce = db.query(Announcement).filter(Announcement.id == id)
    if not delete_announce.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Announcement")
    
    delete_announce.delete()
    db.commit()