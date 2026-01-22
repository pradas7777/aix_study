import uuid
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os
from fastapi import HTTPException, Header
import models
from models import Post
from database import engine, get_db, Base
from fastapi.responses import RedirectResponse


ADMIN_TOKEN = "super-admin-token"

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- 유틸리티 함수 ---
def check_admin(admin_token: Optional[str] = Cookie(None)):
    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin only")


def get_or_create_visitor(db: Session, visitor_uuid: Optional[str] = None):
    """방문자 식별 및 생성"""
    if not visitor_uuid:
        visitor_uuid = str(uuid.uuid4())
        visitor = models.Visitor(visitor_uuid=visitor_uuid)
        db.add(visitor)
        db.commit()
        db.refresh(visitor)
        return visitor, visitor_uuid
    
    visitor = db.query(models.Visitor).filter(models.Visitor.visitor_uuid == visitor_uuid).first()
    if not visitor:
        visitor = models.Visitor(visitor_uuid=visitor_uuid)
        db.add(visitor)
        db.commit()
        db.refresh(visitor)
    
    return visitor, visitor_uuid

# --- 라우트 (페이지) ---
@app.get("/admin/login")
def admin_login(token: str):
    response = RedirectResponse(url="/", status_code=302)

    if token == ADMIN_TOKEN:
        response.set_cookie(
            key="admin_token",
            value=token,
            httponly=True
        )

    return response

@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    visitor_uuid: Optional[str] = Cookie(None),
):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)

    is_admin = admin_token == ADMIN_TOKEN

    # 각 게시판 최신글
    summaries = db.query(models.Post)\
        .filter(models.Post.type == "summary")\
        .order_by(models.Post.created_at.desc())\
        .limit(5).all()

    qnas = db.query(models.Post)\
        .filter(models.Post.type == "qna")\
        .order_by(models.Post.created_at.desc())\
        .limit(5).all()

    lounges = db.query(models.Post)\
        .filter(models.Post.type == "lounge")\
        .order_by(models.Post.created_at.desc())\
        .limit(5).all()

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "visitor": visitor,
            "is_admin": is_admin,
            "summaries": summaries,
            "qnas": qnas,
            "lounges": lounges,
        }
    )

    # ✅ 방문자 쿠키 유지
    response.set_cookie(
        key="visitor_uuid",
        value=v_uuid,
        max_age=60 * 60 * 24 * 365,  # 1년
        httponly=True
    )

    return response

@app.get("/board/{post_type}", response_class=HTMLResponse)
async def board_list(post_type: str, request: Request, db: Session = Depends(get_db), visitor_uuid: Optional[str] = Cookie(None)):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)
    posts = db.query(models.Post).filter(models.Post.type == post_type).order_by(models.Post.created_at.desc()).all()
    
    titles = {"summary": "수업 요약", "qna": "질문 답변", "lounge": "자유 게시판"}
    board_title = titles.get(post_type, "게시판")
    
    return templates.TemplateResponse("board.html", {
        "request": request, 
        "posts": posts, 
        "post_type": post_type, 
        "board_title": board_title,
        "visitor": visitor
    })

@app.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail(post_id: int, request: Request, db: Session = Depends(get_db), visitor_uuid: Optional[str] = Cookie(None)):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return templates.TemplateResponse("detail.html", {"request": request, "post": post, "visitor": visitor})

# --- API (데이터 처리) ---

@app.post("/post/create")
async def create_post(
    type: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    visitor_uuid: Optional[str] = Cookie(None)
):
    # 익명 사용자 가져오기
    visitor, _ = get_or_create_visitor(db, visitor_uuid)

    # 게시글 생성
    new_post = Post(
        type=type,
        title=title,
        content=content,
        visitor_id=visitor.id,   # ✅ visitor 사용
    )

    db.add(new_post)
    db.commit()

    return RedirectResponse(
        url=f"/board/{type}",
        status_code=303
    )
@app.post("/post/{post_id}/delete")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
):
    # 🔒 관리자만
    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin only")

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return RedirectResponse(url="/", status_code=303)



@app.post("/post/{post_id}/comment")
async def create_comment(
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    visitor_uuid: Optional[str] = Cookie(None)
):
    visitor, _ = get_or_create_visitor(db, visitor_uuid)
    
    new_comment = models.Comment(
        content=content,
        post_id=post_id,
        visitor_id=visitor.id
    )
    db.add(new_comment)
    db.commit()
    return RedirectResponse(url=f"/post/{post_id}", status_code=303)

@app.post("/visitor/nickname")
async def update_nickname(
    nickname: str = Form(...),
    db: Session = Depends(get_db),
    visitor_uuid: Optional[str] = Cookie(None)
):
    visitor, _ = get_or_create_visitor(db, visitor_uuid)
    visitor.nickname = nickname
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/admin/enter")
def admin_enter():
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="admin_token",
        value=ADMIN_TOKEN,
        httponly=True
    )
    return response
