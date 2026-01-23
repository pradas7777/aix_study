신림 aix 커뮤니티 웹페이지 (파이썬 + FastAPI + SQLAlchemy + MySQL)

# 핵심 요구사항 및 설계
백엔드
//실행 : Python + FastAPI 
//데이터베이스 : MySQL (SQLAlchemy 사용)
//서버 : 오라클 +  uvicorn + ubuntu @158.179.173.82
프론트엔드
//css html Jinja2Templates

# 핵심 기능
// 로그인 비밀번호 없이 누구나 참여 (쿠키 기반 익명) 
// 관리자 토큰은 따로 (admin -> 게시물 삭제관리)
1. 핵심 게시판 3개 (수업 요약(summary), 질문 답변(qna), 자유 게시판(lounge) -> 'post' 테이블로
                            이미지는 최대 5장까지 하기위해 따로 post_images, 댓글은 comments
2. 데이터 베이스는 mysql에서 생성 community_db 

# 프로젝트 구조
```
anonymous_board/
├── database.py       # MySQL 연결 설정 및 세션 관리
├── models.py         # SQLAlchemy 데이터베이스 모델 정의 (Visitor, Post, Comment)
├── main.py           # FastAPI 애플리케이션, 라우트, API 로직
├── requirements.txt  # Python 의존성 목록
├── static/
│   └── style.css     # 최소한의 CSS 스타일 (큰 폰트, 단순 레이아웃)
└── templates/
    ├── base.html     # 기본 레이아웃 및 네비게이션
    ├── index.html    # 메인 페이지 (최신 글 목록)
    ├── board.html    # 게시판 목록 및 새 글 작성 폼
    └── detail.html   # 게시글 상세 보기 및 댓글 폼
```

# 설치 및 실행 방법
프로젝트 폴더로 이동하여 필요한 라이브러리를 설치합니다.

```bash
cd aix_study
# requirements.txt 파일이 있다면:
# pip install -r requirements.txt
# 또는 수동 설치:
pip install fastapi uvicorn sqlalchemy pymysql jinja2 python-multipart
```

#데이터베이스 
MySQL 서버에 접속하여 데이터베이스를 생성합니다. `database.py` 파일에 설정된 
기본 데이터베이스 이름은 `community_db`입니다.

```sql
-- MySQL 콘솔에서 실행
CREATE DATABASE community_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

**주의**: `database.py` 파일의 `SQLALCHEMY_DATABASE_URL`을 사용자 환경에 맞게 수정해야 합니다. (예: 사용자 이름, 비밀번호, 포트 등)

```python
# database.py (수정 필요)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://aix:1234tlsfla@localhost:3306/community_db?charset=utf8mb4"
# 예: 비밀번호가 'mypass'라면:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mypass@localhost:3306/community_db?charset=utf8mb4"
```

# 테스트 실행

Uvicorn을 사용하여 FastAPI 애플리케이션을 실행합니다.

```bash
uvicorn main:app --reload
```
서버가 시작되면 웹 브라우저에서 `http://127.0.0.1:8000`으로 접속할 수 있습니다.


# git에 업로드
git status
git add .
git commit -m "수정내용"
git push
