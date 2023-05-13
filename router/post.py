from sqlalchemy.orm import Session
from auth.oauth2 import get_current_user
from db.database import get_db
from fastapi import APIRouter, Depends
from typing import Optional
from db.models import Post
from schemas import UserInfoBase, PostDisplay
from db import db_post

router = APIRouter(
    prefix="/post",
    tags=["post"]
)

@router.get('/')
def get_post_list(type: str, search: Optional[str] = None, db: Session = Depends(get_db)):
    return db_post.get_post(type, search, db)

@router.get('/{id}')
def getPostInfo(id: int, db: Session = Depends(get_db)):
    postinfo = db.query(Post).filter(Post.id == id).first()
    return postinfo


@router.post('/')
async def register(post: PostDisplay, current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
    return db_post.register_post(post, current_user, db)

@router.put('/{id}')
def updatePost(id: int, post: PostDisplay, current_user: UserInfoBase = Depends(get_current_user), db: Session = Depends(get_db)):
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