# 익명 커뮤니티 게시판 프로젝트 (FastAPI + SQLAlchemy + MySQL)

## 1. 프로젝트 개요

본 프로젝트는 **Python FastAPI** 프레임워크와 **SQLAlchemy ORM**을 사용하여 구축된 간단한 익명 커뮤니티 웹사이트입니다. 데이터베이스로는 **MySQL**을 사용하며, 프론트엔드는 **Jinja2 템플릿**과 최소한의 CSS로 구성되어 있습니다.

**핵심 요구사항 준수 사항:**
*   **백엔드**: Python FastAPI
*   **데이터베이스**: MySQL (SQLAlchemy ORM 사용)
*   **인증**: 로그인/비밀번호 시스템 없이 **쿠키 기반 익명 사용자 식별**
*   **프론트엔드**: Jinja2 템플릿, 단순한 디자인 (고령자 친화적)
*   **게시판 유형**: 수업 요약(summary), 질문 답변(qna), 자유 게시판(lounge)을 하나의 `Post` 테이블로 관리

## 2. 필수 요구사항

프로젝트를 실행하기 위해서는 다음 환경이 필요합니다.

*   **Python 3.8+**
*   **MySQL 서버** (로컬 또는 원격)

## 3. 프로젝트 구조

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

## 4. 설치 및 실행 방법

### 4.1. Python 의존성 설치

프로젝트 폴더로 이동하여 필요한 라이브러리를 설치합니다.

```bash
cd anonymous_board
# requirements.txt 파일이 있다면:
# pip install -r requirements.txt
# 또는 수동 설치:
pip install fastapi uvicorn sqlalchemy pymysql jinja2 python-multipart
```

### 4.2. MySQL 데이터베이스 설정

MySQL 서버에 접속하여 데이터베이스를 생성합니다. `database.py` 파일에 설정된 기본 데이터베이스 이름은 `community_db`입니다.

```sql
-- MySQL 콘솔에서 실행
CREATE DATABASE community_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

**주의**: `database.py` 파일의 `SQLALCHEMY_DATABASE_URL`을 사용자 환경에 맞게 수정해야 합니다. (예: 사용자 이름, 비밀번호, 포트 등)

```python
# anonymous_board/database.py (수정 필요)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://aix:1234tlsfla@localhost:3306/community_db?charset=utf8mb4"
# 예: 비밀번호가 'mypass'라면:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:mypass@localhost:3306/community_db?charset=utf8mb4"
```

### 4.3. 프로젝트 실행

Uvicorn을 사용하여 FastAPI 애플리케이션을 실행합니다.

```bash
uvicorn main:app --reload
```

서버가 시작되면 웹 브라우저에서 `http://127.0.0.1:8000`으로 접속할 수 있습니다.

## 5. 주요 파일 설명

| 파일명 | 역할 | 주요 내용 |
| :--- | :--- | :--- |
| `database.py` | 데이터베이스 연결 | SQLAlchemy 엔진 및 세션 설정, MySQL 연결 URL 정의 |
| `models.py` | 데이터 모델 | `Visitor`, `Post`, `Comment` 테이블 정의 |
| `main.py` | 애플리케이션 로직 | FastAPI 앱 인스턴스, 정적 파일/템플릿 설정, 방문자 식별 로직, 페이지 라우트 (`/`, `/board/{type}`, `/post/{id}`), 데이터 처리 API (`/post/create`, `/post/{id}/comment`, `/visitor/nickname`) |
| `templates/` | HTML 템플릿 | Jinja2를 사용한 웹 페이지 구조 정의 |
| `static/style.css` | 스타일 | 고령자 친화적인 큰 폰트와 단순한 레이아웃 스타일 |

## 6. API 요청 예시

본 프로젝트는 웹 브라우저의 폼 제출을 통해 모든 데이터 처리가 이루어지도록 설계되었습니다. 따라서 별도의 JSON API 호출보다는 **HTML 폼 기반의 POST 요청**이 주를 이룹니다.

### 6.1. 새 게시글 작성 (POST)

게시판 페이지 (`/board/{type}`)의 폼을 통해 요청됩니다.

*   **URL**: `/post/create`
*   **메서드**: `POST`
*   **폼 데이터 (Form Data)**:
    *   `type`: 게시판 유형 (`summary`, `qna`, `lounge` 중 하나)
    *   `title`: 게시글 제목
    *   `content`: 게시글 내용

### 6.2. 댓글 작성 (POST)

게시글 상세 페이지 (`/post/{id}`)의 폼을 통해 요청됩니다.

*   **URL**: `/post/{post_id}/comment` (예: `/post/1/comment`)
*   **메서드**: `POST`
*   **폼 데이터 (Form Data)**:
    *   `content`: 댓글 내용

### 6.3. 닉네임 변경 (POST)

모든 페이지 상단의 닉네임 변경 폼을 통해 요청됩니다.

*   **URL**: `/visitor/nickname`
*   **메서드**: `POST`
*   **폼 데이터 (Form Data)**:
    *   `nickname`: 변경할 새 닉네임
