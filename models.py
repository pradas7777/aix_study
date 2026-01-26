from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Visitor(Base):
    """익명 방문자 테이블"""
    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)
    visitor_uuid = Column(String(100), unique=True, index=True) # 쿠키에 저장될 고유 ID
    nickname = Column(String(50), default="익명")
    created_at = Column(DateTime, default=datetime.now)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    author = relationship("Visitor", back_populates="posts")
    files = relationship("PostFile", back_populates="post")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    image_url = Column(String(500))
    post = relationship("Post", back_populates="images")

class Comment(Base):
    """댓글 테이블"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    post_id = Column(Integer, ForeignKey("posts.id"))
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    
    post = relationship("Post", back_populates="comments")
    author = relationship("Visitor", back_populates="comments")

#파일첨부 기능 추가
class PostFile(Base):
    __tablename__ = "post_files"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    filename = Column(String(255))    
    original_name = Column(String(255)) 

    post = relationship("Post", back_populates="files")

