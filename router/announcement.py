from sqlalchemy.orm import Session
from db.database import get_db
from fastapi import APIRouter, Depends
from db.models import Announcement

router = APIRouter(
    prefix="/announcement",
    tags=["announcement"]
)

@router.get('/')
def get_announcement_list(db: Session = Depends(get_db)):
    announcement = db.query(Announcement).filter().all()
    return announcement