from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from schemas import PostDisplay, UserInfoBase, PostUpdate
from db.models import BlockList, Post, User, Like
from fastapi import HTTPException, status
from enum import Enum

class PostType(str, Enum):
    rent = "rent"
    lend = "lend"
    share = "share"

def get_post(type: str, search: str, current_user: UserInfoBase | None, db:Session):
    if search:
        search = '%%{}%%'.format(search)
        postlist = db.query(Post).filter(Post.type == type)\
            .filter(Post.title.ilike(search) | Post.content.ilike(search)).all()
    else:
        postlist = db.query(Post).filter(Post.type == type).all()
    if not postlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")

    for post in postlist:
        author = db.query(User).filter(post.author_id == User.id).first()
        post.nickname = author.nickname
        
    for post in postlist:
        if current_user:
            isliked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first()
            if not isliked: post.islike = False
            else: post.islike = True
        else: post.islike = False      

        
    postdisplay = postlist
    
    if current_user:
        postdisplay = []
        for post in postlist:
            isblocked = db.query(BlockList).filter(BlockList.block_id == post.author_id, BlockList.user_id == current_user.id).first()
            if not isblocked: postdisplay.append(post)
            
    return postdisplay


def register_post(post: PostDisplay, current_user: UserInfoBase, db:Session):
    user = db.query(User).filter(User.nickname == current_user.nickname).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Valid User")
    
    if post.type == PostType.share:
        if post.price != 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Share Post price should be 0!")    
    else:
        if post.price <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Price should be more than 0!")
    
    new_post=Post(type = post.type,                 
                  status = post.status,     
                  title = post.title,
                  price = post.price,
                  photo = post.photo,
                  content = post.content, 
                  like_count = post.like_count,
                  created_at = post.created_at,
                  updated_at = post.updated_at,
                  category = post.category,
                  author_id = current_user.id)
                  
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def update_post(id: int, post: PostUpdate, current_user: UserInfoBase, db:Session):
    db_post = db.query(Post).filter(Post.author_id == current_user.id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not Auth User")
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
        
    if post.type == PostType.share:
        if post.price != 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Share Post price should be 0!")    
    else:
        if post.price <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Price should be more than 0!")
            
    db_post.type = post.type
    db_post.title = post.title
    db_post.status = post.status
    db_post.price = post.price
    db_post.photo = post.photo
    db_post.content = post.content
    db_post.updated_at = post.updated_at
    db_post.category = post.category
    db.add(db_post)
    db.commit()
    
def delete_post(id: int, current_user: UserInfoBase, db: Session):
    db_post = db.query(Post).filter(Post.author_id == current_user.id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not Auth User")
        
    delete_post = db.query(Post).filter(Post.id == id)
    if not delete_post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
    
    delete_post.delete(synchronize_session=False)
    db.commit()
    
def like_post(post_id: int, current_user: UserInfoBase, db: Session):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
    
    if db_post.author_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You can't like your post!")
        
    like_exist = db.query(Like).filter(Like.post_id == post_id).filter(Like.user_id == current_user.id)
    if like_exist.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Already Like Post")
    db_post.like_count = db.query(Like).filter(Like.post_id == post_id).count()
    db_post.like_count += 1
    db.add(db_post)
    
    new_like = Like(user_id = current_user.id,                 
                    post_id = post_id) 
    db.add(new_like)    
    db.commit()
    db.refresh(new_like)
    return new_like
 
def delete_like_post(post_id: int, current_user: UserInfoBase, db: Session):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
        
    like_exist = db.query(Like).filter(Like.post_id == post_id).filter(Like.user_id == current_user.id)
    if not like_exist.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Like Not Exist")
    db_post.like_count = db.query(Like).filter(Like.post_id == post_id).count()
    db_post.like_count -= 1
    db.add(db_post)
    
    like_exist.delete(synchronize_session=False)
    db.commit()     