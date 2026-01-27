import uuid
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import Optional
import os
from fastapi import HTTPException, Header
import models
from models import Post
from database import engine, get_db, Base
from fastapi.responses import RedirectResponse
from fastapi import File, UploadFile 
import shutil 
from typing import List


UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
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
    
    studies = db.query(models.Post)\
        .filter(models.Post.type == "study")\
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
            "studies": studies,
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
async def board_list(
    post_type: str, 
    request: Request, 
    db: Session = Depends(get_db), 
    admin_token: Optional[str] = Cookie(None), # 쿠키에서 관리자 토큰을 가져옵니다.
    visitor_uuid: Optional[str] = Cookie(None)
):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)
    
    # 관리자인지 확인하는 변수입니다. (토큰이 일치하면 True, 아니면 False)
    is_admin = admin_token == ADMIN_TOKEN 
    
    posts = db.query(models.Post).filter(models.Post.type == post_type).order_by(models.Post.created_at.desc()).all()
    
    titles = {"summary": "수업 요약", "qna": "질문 답변", "lounge": "자유 게시판", "study" : "그룹 스터디", "suggestion": "사이트 기능 건의"}
    board_title = titles.get(post_type, "게시판")
    
    return templates.TemplateResponse("list.html", {
        "request": request, 
        "posts": posts, 
        "post_type": post_type, 
        "board_title": board_title,
        "visitor": visitor,
        "is_admin": is_admin # 템플릿(HTML)에서 쓸 수 있도록 전달합니다.
    })
@app.get("/board/{post_type}/write", response_class=HTMLResponse)
async def write_page(
    post_type: str, 
    request: Request, 
    db: Session = Depends(get_db),
    visitor_uuid: Optional[str] = Cookie(None)
):
    visitor, _ = get_or_create_visitor(db, visitor_uuid)
    titles = {"summary": "수업 요약", "qna": "질문 답변", "lounge": "자유 게시판", "study" : "그룹 스터디", "suggestion": "사이트 기능 건의"}
    board_title = titles.get(post_type, "게시판")
    
    # 기존의 글쓰기 폼이 들어있는 board.html을 보여줍니다.
    return templates.TemplateResponse("board.html", {
        "request": request, 
        "post_type": post_type, 
        "board_title": board_title,
        "visitor": visitor
    })
@app.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail(
    post_id: int, 
    request: Request, 
    db: Session = Depends(get_db), 
    admin_token: Optional[str] = Cookie(None), # 관리자 토큰 가져오기
    visitor_uuid: Optional[str] = Cookie(None)

):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)

    db.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(views=Post.views + 1)
    )
    db.commit()
    # 관리자 여부 확인
    is_admin = admin_token == ADMIN_TOKEN

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return templates.TemplateResponse("detail.html", {
        "request": request, 
        "post": post, 
        "visitor": visitor,
        "is_admin": is_admin, # 템플릿에 관리자 여부 전달
        "current_visitor_id": visitor.id
    })
# --- API (데이터 처리) ---
@app.get("/post/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_page(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    visitor_uuid: Optional[str] = Cookie(None),
):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)

    is_admin = admin_token == ADMIN_TOKEN

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # ✅ 권한 체크: 관리자 OR 작성자만 수정 가능
    if (not is_admin) and (post.visitor_id != visitor.id):
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    return templates.TemplateResponse("edit.html", {
        "request": request,
        "post": post,
        "visitor": visitor,
        "is_admin": is_admin
    })
@app.post("/post/{post_id}/edit")
async def edit_post_save(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    visitor_uuid: Optional[str] = Cookie(None),
):
    visitor, v_uuid = get_or_create_visitor(db, visitor_uuid)

    is_admin = admin_token == ADMIN_TOKEN

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # ✅ 권한 체크: 관리자 OR 작성자만 저장 가능
    if (not is_admin) and (post.visitor_id != visitor.id):
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    post.title = title
    post.content = content
    db.commit()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)

@app.post("/post/create")
async def create_post(
    type: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    images: List[UploadFile] = File(None), # 여러 파일을 리스트로 받습니다.
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    visitor_uuid: Optional[str] = Cookie(None)
):
    # 1. 익명 사용자 정보를 가져옵니다.
    visitor, _ = get_or_create_visitor(db, visitor_uuid)

    # 2. 게시글 객체를 생성합니다. (image_url은 여기서 넣지 않습니다!)
    new_post = Post(
        type=type,
        title=title,
        content=content,
        visitor_id=visitor.id,
    )

    db.add(new_post)
    # 3. flush()를 호출하여 DB에 임시로 저장하고 생성된 게시글의 ID(new_post.id)를 확보합니다.
    db.flush()

    # 4. 첨부된 이미지들이 있다면 처리합니다.
    if images:
        # 최대 5장까지만 반복문을 돕니다.
        for img in images[:5]:
            # 파일명이 있는 실제 파일인지 확인합니다.
            if img.filename and img.filename.strip():
                # 서버에 저장할 고유한 파일 이름을 만듭니다.
                file_name = f"{uuid.uuid4()}_{img.filename}"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                
                # 실제로 파일을 서버 폴더에 저장합니다.
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                
                # 5. DB의 이미지 테이블(PostImage)에 정보를 저장합니다.
                # 웹상에서 접근 가능한 경로인 "/static/uploads/..." 형태로 저장합니다.
                new_image = models.PostImage(
                    post_id=new_post.id, 
                    image_url=f"/static/uploads/{file_name}"
                )
                db.add(new_image)

    # 6. 일반 첨부파일이 있다면 처리합니다
    if file and file.filename and file.filename.strip():
        # 서버에 저장할 고유한 파일 이름을 만듭니다.
        gen_file_name = f"{uuid.uuid4()}_{file.filename}"
        gen_file_path = os.path.join(UPLOAD_DIR, gen_file_name)
        
        # 파일을 실제로 서버의 uploads 폴더에 저장합니다.
        with open(gen_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # DB의 파일 테이블(PostFile)에 정보를 저장합니다.
        new_file = models.PostFile(
            post_id=new_post.id,
            filename=gen_file_name,      # 서버 저장용 이름
            original_name=file.filename  # 사용자가 올린 원래 이름 (다운로드용)
        )
        db.add(new_file)


    # 7. 모든 변경사항을 최종적으로 DB에 반영합니다.
    db.commit()

    # 완료 후 해당 게시판 목록으로 이동합니다.
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
    post_type = post.type
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return RedirectResponse(
        url=f"/board/{post_type}",
        status_code=303
    )

@app.post("/post/image/upload")
async def upload_editor_image(file: UploadFile = File(...)):
    # 1. 파일에 고유한 이름을 붙입니다.
    file_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # 2. 서버의 uploads 폴더에 실제로 파일을 저장합니다.
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 3. 에디터가 이미지 주소로 사용할 수 있게 경로를 반환합니다.
    return {"url": f"/static/uploads/{file_name}"}

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

@app.post("/comment/{comment_id}/delete")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    admin_token: Optional[str] = Cookie(None),
    visitor_uuid: Optional[str] = Cookie(None),
):
    # 0) 댓글 조회
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    # 1) 관리자 검사 (우선)
    try:
        check_admin(admin_token)  # admin_token != ADMIN_TOKEN 이면 403 발생
        post_id = comment.post_id
        db.delete(comment)
        db.commit()
        return RedirectResponse(url=f"/post/{post_id}", status_code=303)
    except HTTPException:
        pass  # 관리자 아니면 작성자 검사로 진행

    # 2) 작성자 검사
    if not visitor_uuid:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    visitor, _ = get_or_create_visitor(db, visitor_uuid)
    if comment.visitor_id != visitor.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    post_id = comment.post_id
    db.delete(comment)
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
