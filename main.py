from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from router import announcement, chat, post, user
from auth import authentication

from db import models
from db.database import engine

app = FastAPI()

app.include_router(authentication.router)
app.include_router(announcement.router)
app.include_router(chat.router)
app.include_router(post.router)
app.include_router(user.router)

models.Base.metadata.create_all(bind=engine)

app.mount('/images', StaticFiles(directory="static/images"))

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)