from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    nickname = Column(String(10), nullable=False, unique=True)
    loc = Column(Boolean, nullable=False)
    thumbnail = Column(String(255), nullable=False)
    is_activate = Column(Boolean, nullable=False, default=False)
    is_ban = Column(Boolean, nullable=False, default=False)
    report_count = Column(Integer, nullable=False, default=0)
    role = Column(Boolean, nullable=False, default=False)

    post = relationship('Post', back_populates='user', cascade="all, delete")
    blocklist = relationship('BlockList', back_populates='user', cascade="all, delete")
    reportlog = relationship('ReportLog', back_populates='user', cascade="all, delete")
    like = relationship('Like', back_populates='user', cascade="all, delete")
    chatroom = relationship('ChatRoom', back_populates='user', cascade="all, delete")
    chatmessage = relationship('ChatMessage', back_populates='user', cascade="all, delete")

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum('rent', 'lend', 'share'), nullable=False)
    status = Column(Enum('possible', 'progress', 'done'), nullable=False)
    title = Column(String(30), nullable=False)
    price = Column(Integer, nullable=False)
    photo = Column(String(255), nullable=False)
    content = Column(String(1000), nullable=False)
    like_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())

    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)

    user = relationship('User', back_populates='post', cascade="all, delete")
    category = relationship('Category', back_populates='post')
    like = relationship('Like', back_populates='post', cascade="all, delete")


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key= True, index= True)
    name = Column(String(30), nullable=False)

    post = relationship('Post', back_populates='category')

class BlockList(Base):
    __tablename__ = 'blocklist'

    id = Column(Integer, primary_key=True, index= True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)
    block_id = Column(Integer, nullable = False)
    created_at = Column(DateTime, nullable = False, default=datetime.now())

    user = relationship('User', back_populates='blocklist')

class ReportLog(Base):
    __tablename__ = 'reportlog'

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)
    report_id = Column(Integer, nullable = False)

    user = relationship('User', back_populates='reportlog')
class Like(Base):
    __tablename__ = 'like'

    id = Column(Integer, primary_key=True, index= True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)
    post_id = Column(Integer, ForeignKey('post.id', ondelete='cascade'), nullable = False)

    user = relationship('User', back_populates='like')
    post = relationship('Post', back_populates='like')

class ChatRoom(Base):
    __tablename__ = 'chatroom'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)
    receiver_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)

    user = relationship('User', back_populates='chatroom', cascade="all, delete")
    chatmessage = relationship('ChatMessage', back_populates='chatroom', cascade="all, delete")

class ChatMessage(Base):
    __tablename__ = 'chatmessage'

    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey('chatroom.id', ondelete='cascade'), nullable = False)
    sender_id = Column(Integer, ForeignKey('user.id', ondelete='cascade'), nullable = False)
    message = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    chatroom = relationship('ChatRoom', back_populates='chatmessage', cascade="all, delete")
    user = relationship('User', back_populates='chatmessage', cascade="all, delete")
    

class Announcement(Base):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), nullable=False)
    content = Column(String(1000), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
