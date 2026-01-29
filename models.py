from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
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
    views = Column(Integer, nullable=False, default=0)
    has_poll = Column(Boolean, default=False, nullable=False)
    poll_options = relationship(
        "PollOption",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="PollOption.order"
    )

class Voter(Base):
    """
    ✅ 실명 화이트리스트 테이블
    - 미리 이름들을 넣어둬야 함
    """
    __tablename__ = "voter"

    id = Column(Integer, primary_key=True, index=True)
    realname = Column(String(50), unique=True, index=True, nullable=False)

class Vote(Base):
    """
    ✅ 게시글마다 1회 투표 (변경 가능)
    - (post_id, voter_id) 유니크로 1회 보장
    """
    __tablename__ = "vote"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True, nullable=False)
    option_id = Column(Integer, ForeignKey("poll_option.id"), index=True, nullable=False)
    voter_id = Column(Integer, ForeignKey("voter.id"), index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("post_id", "voter_id", name="uq_vote_once_per_post"),
    )

class PollOption(Base):
    __tablename__ = "poll_option"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True, nullable=False)

    text = Column(String(200), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    vote_count = Column(Integer, default=0, nullable=False)

    post = relationship("Post", back_populates="poll_options")

class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    image_url = Column(String(500))
    post = relationship("Post", back_populates="images")

class Comment(Base):
    """댓글 및 대댓글 테이블"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    visitor_id = Column(Integer, ForeignKey("visitors.id"))
    
    # ✅ 대댓글용: 부모 댓글 id
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    post = relationship("Post", back_populates="comments")
    author = relationship("Visitor", back_populates="comments")

    # ✅ 셀프 참조 관계 설정
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Comment.created_at"
    )

#파일첨부 기능 추가
class PostFile(Base):
    __tablename__ = "post_files"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    filename = Column(String(255))    
    original_name = Column(String(255)) 

    post = relationship("Post", back_populates="files")

