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

class ProfileBase(BaseModel):
    thumbnail: str
    nickname: str
    loc: bool
    loc_str: str
    class Config():
        orm_mode = True