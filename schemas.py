from typing import Dict, List, Optional
from datetime import date
from pydantic import BaseModel

# Schema 작성
class AnnouncementBase(BaseModel):
    title: str
    content: str