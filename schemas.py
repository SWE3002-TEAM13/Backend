from typing import Dict, List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum

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

class PostDisplay(BaseModel):
    type: PostType
    title : str
    status : PostStatusEnum
    price : int
    photo : str
    content : str
    like_count : int
    created_at : datetime
    updated_at : datetime
    nickname : str
    category: CategoryEnum
    class Config():
        orm_mode = True
       
class AnnounceDisplay(BaseModel):
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
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
    