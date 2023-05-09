import shutil
from auth.oauth2 import get_current_user
from db.database import get_db
from fastapi import APIRouter, Depends, UploadFile, File, Form
from schemas import ProfileBase, UserCreateBase, ProfileUpdateBase
from sqlalchemy.orm import Session
from db import db_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post('/register')
def register(username: str = Form(...), password: str = Form(...), email: str = Form(...), nickname: str = Form(...),
            loc: bool = Form(...), thumbnail: UploadFile = File(...), db: Session = Depends(get_db)):
    path = f"images/{image.filename}"
    with open(path, 'w+b') as buffer:
        shutil.copyfileobj(image.file, buffer)
    return {
        'filename': image.filename
    }
    return db_user.register(request, db)

@router.get('/profile', response_model = ProfileBase)
def getProfile(current_user: ProfileBase = Depends(get_current_user)):
        
    if current_user.loc: current_user.loc_str="자연과학캠퍼스(율전)"
    else: current_user.loc_str="인문사회과학캠퍼스(명륜)"
    
    return current_user

@router.put('/profile')
def updateProfile(request: ProfileUpdateBase, db: Session = Depends(get_db),
                  current_user = Depends(get_current_user)):

    return db_user.updateProfile(request, current_user,db)
    

@router.get('/profile/{name}', response_model=ProfileBase)
def getProfileInfo(name: str, db: Session = Depends(get_db)):
    
    user = db_user.getUserByNickname(name, db)
        
    if user.loc: user.loc_str="자연과학캠퍼스(율전)"
    else: user.loc_str="인문사회과학캠퍼스(명륜)"
    
    return user

@router.post('/block/{id}')
def blockUser(id : int, db: Session = Depends(get_db),
              current_user = Depends(get_current_user)):
    pass

@router.delete('/block/{id}')
def deleteBlockedUser(id : int, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    pass

@router.post('/report/{id}')
def reportUser(id: int, db: Session = Depends(get_db),
               current_user = Depends(get_current_user)):
    
    pass

