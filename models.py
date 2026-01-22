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
    """게시글 테이블 (수업 요약, Q&A, 라운지 통합)"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), index=True) # "summary", "qna", "lounge"
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 작성자 정보 (익명)
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    author = relationship("Visitor", back_populates="posts")
    
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

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
