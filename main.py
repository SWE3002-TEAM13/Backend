from fastapi import FastAPI
from router import announcement, chat, lend, rent, share, user
from sqlalchemy.orm import Session

from db import models
from db.database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(announcement.router)
app.include_router(chat.router)
app.include_router(lend.router)
app.include_router(rent.router)
app.include_router(share.router)
app.include_router(user.router)
