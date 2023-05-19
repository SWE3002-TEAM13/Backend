import os
import shutil
from datetime import datetime
import smtplib
from typing import Optional

from dotenv import load_dotenv
from auth.oauth2 import get_current_user
from db.database import get_db
from fastapi import APIRouter, BackgroundTasks, Depends, Request, UploadFile, File, Form, HTTPException, status
from db.hash import Hash
from schemas import BlockUserDisplay, MyProfileBase, OtherProfileBase, UserCreateBase, ProfileUpdateBase, UserInfoBase
from sqlalchemy.orm import Session
from db import db_user
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, '../static/images')
SERVER_IMG_DIR = os.path.join('http://localhost:8000/', 'images/')

load_dotenv()

async def send_email(to_email, username, base_url, verification_token):
    from_email = os.getenv("MAIL_USERNAME")
    app_password = os.getenv("MAIL_PASSWORD")


    msg = MIMEMultipart()
    body = f'<html><body><p>해당 링크를 눌러 회원가입을 완료하세요!:\
             <a href="http://localhost:3000/verify?token={verification_token}&username={username}">http://localhost:3000/verify?token={verification_token}&username={username}</a></p></body></html>'

    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = '회원가입 인증 메일 [성균:나누Re]'
    msg.attach(MIMEText(body, 'html'))

    smtp_server = 'smtp.gmail.com'
    port = 587

    smtpObj = smtplib.SMTP(smtp_server, port)
    smtpObj.starttls()
    smtpObj.login(from_email, app_password)
    text = msg.as_string()
    smtpObj.sendmail(from_email, to_email, text)
    smtpObj.quit()

async def send_verification_email(user_email, verification_token, username, base_url, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, user_email, username, base_url, verification_token)


def thumbnail_upload(thumbnail: UploadFile = File(...)):
    if thumbnail:
        new_name = datetime.now().strftime('%Y%m%d%H%M%S') + thumbnail.filename
        dir_path = os.path.join(IMG_DIR, new_name)
        server_path = os.path.join(SERVER_IMG_DIR, new_name)
        with open(dir_path, 'w+b') as buffer:
            shutil.copyfileobj(thumbnail.file, buffer)
        return server_path
    else:
        return os.path.join(SERVER_IMG_DIR, "logo.jpg")

@router.post('/register')
async def register(background_tasks: BackgroundTasks, request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), nickname: str = Form(...),
            loc: bool = Form(...), thumbnail: Optional[UploadFile] = None, db: Session = Depends(get_db)):
    
    path = thumbnail_upload(thumbnail)

    user = UserCreateBase(username=username, password=password, email=email, nickname=nickname, loc=loc, thumbnail=path)

    db_user.register(user, db)

    await send_verification_email(user.email, Hash.bcrypt(user.email), user.username, request.base_url, background_tasks)

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

@router.get('/me')
def getMyUserId(current_user: UserInfoBase = Depends(get_current_user)):
    
    return {"id" : current_user.id, "nickname" :current_user.nickname}
    

@router.get('/profile/{id}', response_model= OtherProfileBase)
def getProfileInfo(id: int, db: Session = Depends(get_db)):
    
    profile = db_user.getUser(id, db)
    if profile.loc: profile.loc_str="자연과학캠퍼스(율전)"
    else: profile.loc_str="인문사회과학캠퍼스(명륜)"

    rent_list = db_user.getRentList(id, db)
    lend_list = db_user.getLendList(id, db)
    share_list = db_user.getShareList(id, db)
    
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

