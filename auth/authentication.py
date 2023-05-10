from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from db import models, db_user
from db.hash import Hash
from auth import oauth2


router = APIRouter(tags=["authentication"])

# OAuth2PasswordRequestForm Format
# username / password
@router.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Invalid Credentials") 
    if not Hash.verify(user.password, request.password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Incorrect password") 
    if user.is_ban:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User is Banned!")
    
    if not user.is_activate:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Verify Email First!")            
    # generate a JWT token and return
    access_token = oauth2.create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/verify')
def verify(token: str, username: str, db: Session = Depends(get_db)):

    user = db_user.activateUser(token, username, db)

    return user.id