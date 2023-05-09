import os
import shutil
from datetime import datetime
from typing import Optional
from auth.oauth2 import get_current_user
from db.database import get_db
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from schemas import BlockUserDisplay, MyProfileBase, OtherProfileBase, UserCreateBase, ProfileUpdateBase, UserInfoBase
from sqlalchemy.orm import Session
from db import db_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, '../static/images')

def thumbnail_upload(thumbnail: UploadFile = File(...)):
    if thumbnail:
        new_name = datetime.now().strftime('%Y%m%d%H%M%S') + thumbnail.filename
        path = os.path.join(IMG_DIR, new_name)
        with open(path, 'w+b') as buffer:
            shutil.copyfileobj(thumbnail.file, buffer)
        return path
    else:
        return os.path.join(IMG_DIR, "logo.jpg")

@router.post('/register')
def register(username: str = Form(...), password: str = Form(...), email: str = Form(...), nickname: str = Form(...),
            loc: bool = Form(...), thumbnail: Optional[UploadFile] = None, db: Session = Depends(get_db)):
    
    path = thumbnail_upload(thumbnail)

    user = UserCreateBase(username=username, password=password, email=email, nickname=nickname, loc=loc, thumbnail=path)

    return db_user.register(user, db)

@router.get('/profile/me', response_model = MyProfileBase)
def getProfile(current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    
    profile = db_user.getUser(current_user.id, db)
    if profile.loc: profile.loc_str="자연과학캠퍼스(율전)"
    else: profile.loc_str="인문사회과학캠퍼스(명륜)"
    
    block_list = db_user.getBlockList(current_user, db)
    block_list_display = []
    for user, created_at in block_list:
        block_list_display.append(BlockUserDisplay(
            id=user.id,
            thumbnail=user.thumbnail,
            nickname=user.nickname,
            created_at=created_at
        ))
    like_list = db_user.getLikeList(current_user, db)
    rent_list = db_user.getRentList(current_user.id, db)
    lend_list = db_user.getLendList(current_user.id, db)
    share_list = db_user.getShareList(current_user.id, db)
    
    return {"profile" : profile, "blocklist": block_list_display, "likelist" : like_list,  "rentlist": rent_list, "lendlist" : lend_list, "share_list": share_list}


@router.get('/profile/{id}', response_model= OtherProfileBase)
def getProfileInfo(id: int, db: Session = Depends(get_db)):
    
    profile = db_user.getUser(id, db)
    if profile.loc: profile.loc_str="자연과학캠퍼스(율전)"
    else: profile.loc_str="인문사회과학캠퍼스(명륜)"

    rent_list = db.user.getRentList(id, db)
    lend_list = db.user.getLendList(id, db)
    share_list = db.user.getShareList(id, db)
    
    return {"profile" : profile, "rentlist": rent_list, "lendlist" : lend_list, "share_list": share_list}


@router.put('/profile')
def updateProfile(nickname: str = Form(...), loc: bool = Form(...), thumbnail: Optional[UploadFile] = None,
                 db: Session = Depends(get_db), current_user: UserInfoBase = Depends(get_current_user)):

    if thumbnail: path = thumbnail_upload(thumbnail)
    else: path = None
    
    profile = ProfileUpdateBase(nickname=nickname, loc=loc, thumbnail=path)
    return db_user.updateProfile(profile, current_user,db)
    

@router.post('/block/{id}')
def blockUser(id : int, db: Session = Depends(get_db),
              current_user: UserInfoBase  = Depends(get_current_user)):
    
    return db_user.createBlock(id, current_user, db)

@router.delete('/block/{id}')
def deleteBlockedUser(id : int, db: Session = Depends(get_db),
                      current_user: UserInfoBase  = Depends(get_current_user)):
    
    return db_user.deleteBlock(id, current_user, db)

@router.post('/report/{id}')
def reportUser(id: int, db: Session = Depends(get_db),
               current_user: UserInfoBase  = Depends(get_current_user)):

    return db_user.reportUser(id, current_user, db)

