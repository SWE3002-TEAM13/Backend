from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from schemas import PostDisplay, UserInfoBase, PostUpdate
from db.models import Post, User, Like
from fastapi import HTTPException, status

def get_post(type: str, search: str, db:Session):
    if search:
        search = '%%{}%%'.format(search)
        post = db.query(Post).filter(Post.type == type)\
            .filter(Post.title.ilike(search) | Post.content.ilike(search)).all()
    else:
        post = db.query(Post).filter(Post.type == type).all()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
    return post

def register_post(post: PostDisplay, current_user: UserInfoBase, db:Session):
    user = db.query(User).filter(User.nickname == current_user.nickname).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Valid User")
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
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Auth User")
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
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
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Auth User")
        
    delete_post = db.query(Post).filter(Post.type == 'lend').filter(Post.id == id)
    if not delete_post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
    
    delete_post.delete()
    db.commit()
    
def like_post(post_id: int, current_user: UserInfoBase, db: Session):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Not Exist Post")
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
                    detail=f"Not Exist Like")
    db_post.like_count = db.query(Like).filter(Like.post_id == post_id).count()
    db_post.like_count -= 1
    db.add(db_post)
    
    like_exist.delete()
    db.commit()     