from sqlalchemy.orm.session import Session
from db.hash import Hash
from schemas import UserCreateBase, ProfileUpdateBase
from db.models import BlockList, Like, Post, User
from fastapi import HTTPException, status

def register(request: UserCreateBase, db: Session):
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

def getUserByUsername(username: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the name {username} is not available")
    return user   

def getUserByNickname(nickname: str, db: Session):
    user = db.query(User).filter(User.nickname == nickname).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the name {nickname} is not available")
    return user 

def updateProfile(request: ProfileUpdateBase, current_user, db: Session):
    user = db.query(User).filter(User.username == username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with username not found")

    return user

def getBlockList(name: str, db: Session):
    user = getUserByNickname(name, db)
    blocklist = db.query(BlockList.id).join(BlockList.user).join(User.id).filter(BlockList.user_id == user.id).all()

    return blocklist

def getLikeList(name: str, db: Session):
    user = getUserByNickname(name, db)
    like = db.query(Like).filter(Like.user_id == user.id).all()

    return like

def getRentList(name: str, db: Session):
    user = getUserByNickname(name, db)
    rentlist = db.query(Post).filter(Post.author_id == user.id).filter(type == 0).all()

    return rentlist

def getLendList(name: str, db: Session):
    user = getUserByNickname(name, db)
    lendlist = db.query(Post).filter(Post.author_id == user.id).filter(type == 1).all()

    return lendlist

def getShareList(name: str, db: Session):
    user = getUserByNickname(name, db)
    sharelist = db.query(Post).filter(Post.author_id == user.id).filter(type == 2).all()

    return sharelist

def createBlock(id: int):
    new_block = BlockList(user_id = id, block_id = id)
    db.add(new_block)
    