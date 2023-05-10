import os
import re
import smtplib
from dotenv import load_dotenv
from sqlalchemy.orm.session import Session
from db.hash import Hash
from schemas import UserCreateBase, ProfileUpdateBase, UserInfoBase
from db.models import BlockList, Like, Post, ReportLog, User
from fastapi import HTTPException, status



def register(request: UserCreateBase, db: Session):
    
    user = db.query(User).filter(User.username == request.username).first()
    email = db.query(User).filter(User.email == request.email).first()
    nickname = db.query(User).filter(User.nickname == request.nickname).first()
    
    if not re.match("^[a-zA-Z0-9_]{5,20}$", request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username must be composed of alphabet, number or underscore, and length must be between 5 and 20.")
    
    if len(request.password) < 8 or request.password.isnumeric():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Invalid Password Format!")
    
    if not (request.email.endswith('@g.skku.edu') or request.email.endswith('@skku.edu')):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Email must end with @g.skku.edu or @skku.edu!")
        
    if len(request.nickname) > 10:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"nickname must be less than 10 characters!")

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Username Exist!")
    if email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Email Exist!")
    if nickname:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Nickname Exist!")

    user = User(
        username = request.username,
        password = Hash.bcrypt(request.password),
        email = request.email,
        nickname = request.nickname,
        loc = request.loc,
        thumbnail = request.thumbnail
    )
        

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def activateUser(token: str, username: str, db: Session):

    user = db.query(User).filter(User.username == username)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Valid User")

    if not Hash.verify(token, user.first().email):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Invalid Token")

    if user.first().is_activate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Token Expired")
    
    user.update({"is_activate" : True})
    db.commit()

    return user.first()

def getUser(id: int, db: Session):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")
    
    return user

def getUserByUsername(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")
    return user   

def updateProfile(request: ProfileUpdateBase, current_user: UserInfoBase, db: Session):
    user = db.query(User).filter(User.id == current_user.id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User not found")
    
    if request.thumbnail is None:
        request.thumbnail = user.first().thumbnail

    user.update(request.dict())
    db.commit()

def getBlockList(current_user: UserInfoBase, db: Session):
    blocklist = db.query(User, BlockList.created_at).join(BlockList, User.id == BlockList.block_id).filter(BlockList.user_id==current_user.id).all()
    
    return blocklist

def getLikeList(current_user: UserInfoBase, db: Session):
    likelist = db.query(Post, User.nickname).join(Like, Post.id == Like.post_id).filter(Like.user_id == current_user.id).all()

    return likelist

def getRentList(id: int, db: Session):
    rentlist = db.query(Post, User.nickname).filter(Post.author_id == id, type == 0).all()

    return rentlist

def getLendList(id: int, db: Session):
    lendlist = db.query(Post, User.nickname).filter(Post.author_id == id, type == 1).all()

    return lendlist

def getShareList(id: int, db: Session):
    sharelist = db.query(Post, User.nickname).filter(Post.author_id == id, type == 2).all()

    return sharelist

def createBlock(id: int, current_user: UserInfoBase, db: Session):
    block_user = db.query(User).filter(User.id == id).first()
    if not block_user or id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not valid id")
    new_block = BlockList(user_id = current_user.id, block_id = id)
    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block

def deleteBlock(id: int, current_user: UserInfoBase, db: Session):
    block_user = db.query(BlockList).filter(BlockList.block_id == id, BlockList.user_id == current_user.id)
    if not block_user.first():        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found") 
    block_user.delete(synchronize_session=False)
    db.commit()

def reportUser(id: int, current_user: UserInfoBase, db: Session):
    report_log = db.query(ReportLog).filter(ReportLog.user_id == current_user.id, ReportLog.report_id == id).first()
    user = db.query(User).filter(User.id == id)

    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    if report_log:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Report Already!")
    if id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You can't report yourself!")

    new_report = ReportLog(user_id = current_user.id, report_id = id)
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    report_cnt = user.first().report_count
    report_cnt += 1

    if report_cnt > 10:
        user.update({"report_count" : report_cnt, "is_ban" : True})
    else:
        user.update({"report_count" : report_cnt})
    db.commit()

