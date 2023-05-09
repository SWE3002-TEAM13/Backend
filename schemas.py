from typing import Dict, List, Optional
from datetime import date
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
    username: str
    class Config():
        orm_mode = True

class ProfileBase(BaseModel):
    thumbnail: str
    nickname: str
    loc: bool
    loc_str: str
    class Config():
        orm_mode = True

class ProfileUpdateBase(BaseModel):
    thumbnail: str
    loc: bool
    class Config():
        orm_mode = True

