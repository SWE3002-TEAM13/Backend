import os
import shutil
from datetime import datetime
import smtplib
from enum import Enum
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from auth.oauth2 import get_current_user, get_current_user_otherwise
from db.database import get_db
from fastapi import APIRouter, Depends, Form, UploadFile, File
from typing import Optional
from db.models import Post, User
from schemas import UserInfoBase, PostDisplay, PostUpdate
from db import db_post

router = APIRouter(
    prefix="/post",
    tags=["post"]
)

class PostType(str, Enum):
    rent = "rent"
    lend = "lend"
    share = "share"
    
class PostStatusEnum(str, Enum):
    possible = "possible"
    progress = "progress"
    done = "done"

class CategoryEnum(str, Enum):
    Electronics = "Electronics"
    Clothes = "Clothes"
    Book = "Book"
    Furniture = "Furniture"
    Food = "Food"
    Other = "Other"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, '../static/images')
SERVER_IMG_DIR = os.path.join('http://localhost:8000/', 'images/')

def photo_upload(photo: UploadFile = File(...)):
    if photo:
        new_name = datetime.now().strftime('%Y%m%d%H%M%S') + photo.filename
        dir_path = os.path.join(IMG_DIR, new_name)
        server_path = os.path.join(SERVER_IMG_DIR, new_name)
        with open(dir_path, 'w+b') as buffer:
            shutil.copyfileobj(photo.file, buffer)
        return server_path
    else:
        return os.path.join(SERVER_IMG_DIR, "logo.jpg")

@router.get('/')
def get_post_list(type: str, search: Optional[str] = None, current_user = Depends(get_current_user_otherwise), db: Session = Depends(get_db)):
    posts = db_post.get_post(type, search, current_user, db)

    return posts
@router.get('/{id}')
def getPostInfo(id: int, db: Session = Depends(get_db)):
    postinfo = db.query(Post).filter(Post.id == id).first()
    if not postinfo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")

    author = db.query(User).filter(postinfo.author_id == User.id).first()
    postinfo.nickname = author.nickname
    return postinfo


@router.post('/')
async def register(type: PostType = Form(...), title: str = Form(...), status: PostStatusEnum = Form(...), price: int = Form(...),
            photo: Optional[UploadFile] = None , content: str = Form(...), category: CategoryEnum = Form(...),
            current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    path = photo_upload(photo)
    post = PostDisplay(type=type, title=title, status=status, price=price, photo=path, content=content, like_count=0, 
                       created_at=datetime.now(), updated_at=datetime.now(), nickname=current_user.nickname, category=category)
    return db_post.register_post(post, current_user, db)

@router.put('/{id}')
def updatePost(id: int, type: PostType = Form(...), title: str = Form(...), status: PostStatusEnum = Form(...), price: int = Form(...),
            photo: Optional[UploadFile] = None , content: str = Form(...), category: CategoryEnum = Form(...), 
            current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    path = photo_upload(photo)
    post = PostUpdate(type=type, title=title, status=status, price=price, photo=path, content=content, 
                       updated_at=datetime.now(), category=category)
    return db_post.update_post(id, post, current_user, db)


@router.delete('/{id}')
def deletePost(id: int, current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return db_post.delete_post(id, current_user, db)
    
@router.post('/{post_id}/like')
def likePost(post_id: int, current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return db_post.like_post(post_id, current_user, db)


@router.delete('/{post_id}/like')
def deletelikePost(post_id: int, current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return db_post.delete_like_post(post_id, current_user, db)