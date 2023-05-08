from db.database import get_db
from fastapi import APIRouter, Depends
from schemas import ProfileBase, UserCreateBase
from sqlalchemy.orm import Session
from db import db_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post('/register')
def register(request: UserCreateBase, db: Session = Depends(get_db)):
    return db_user.register(request, db)

@router.get('/profile')
def getProfile(request: int,db: Session = Depends(get_db)):
    pass

@router.put('/profile')
def updateProfile(request: int, db: Session = Depends(get_db)):
    pass

@router.get('/profile/{name}', response_model=ProfileBase)
def getProfileInfo(name: str, db: Session = Depends(get_db)):
    
    user = db_user.getUser(name, db)
        
    if user.loc: user.loc_str="자연과학캠퍼스(율전)"
    else: user.loc_str="인문사회과학캠퍼스(명륜)"
    
    return user

@router.post('/block/{id}')
def blockUser(id : int, db: Session = Depends(get_db)):
    pass

@router.delete('/block/{id}')
def deleteBlockedUser(id : int, db: Session = Depends(get_db)):
    pass

@router.post('/report/{id}')
def reportUser(id: int, db: Session = Depends(get_db)):
    pass

