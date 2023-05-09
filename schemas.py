from typing import Dict, List, Optional
from datetime import date, datetime
from pydantic import BaseModel

# Schema 작성
class UserCreateBase(BaseModel):
    username: str
    password: str
    email: str
    nickname: str
    loc: bool
    thumbnail: str

class UserInfoBase(BaseModel):
    id : int
    nickname: str
    class Config():
        orm_mode = True

class ProfileUpdateBase(BaseModel):
    nickname: str
    loc: bool
    thumbnail: Optional[str] = None
    class Config():
        orm_mode = True
        
class ProfileDisplay(BaseModel):
    nickname : str
    thumbnail : str
    loc: bool
    loc_str : str
    class Config():
        orm_mode = True
        
class BlockUserDisplay(BaseModel):
    id : int
    thumbnail : str
    nickname : str
    created_at : datetime
    class Config():
        orm_mode = True
class PostDisplay(BaseModel):
    title : str
    status : int
    price : int
    photo : str
    content : str
    like_count : int
    created_at : datetime
    updated_at : datetime
    nickname : str
    class Config():
        orm_mode = True
class MyProfileBase(BaseModel):
    profile : ProfileDisplay
    blocklist : List[BlockUserDisplay] = []
    likelist : List[PostDisplay] = []
    rentlist : List[PostDisplay] = []
    lendlist : List[PostDisplay] = []
    sharelist : List[PostDisplay] = []
    class Config():
        orm_mode = True
        
class OtherProfileBase(BaseModel):
    profile : ProfileDisplay
    rentlist : List[PostDisplay] = []
    lendlist : List[PostDisplay] = []
    sharelist : List[PostDisplay] = []
    class Config():
        orm_mode = True
    