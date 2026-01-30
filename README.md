#신림 aix 커뮤니티 웹페이지 (파이썬 + FastAPI + SQLAlchemy + MySQL)
#본 프로젝트는 오라클 서버를 통해 구동 되며 기본 주소는 아래와 같습니다
#http://158.179.173.82/

**본 사이트는 학생들을 위한 자유로운 정보 공유 및 수업 효과 향상을 위해 개설하였습니다**
**또한 학생들이 직접 사이트를 개발 및 관리하고 협업하는 연습을 하고자 함에 개발 목적이 있습니다**
**따라서 신림aix 학생이라면 누구든지 개발 및 운영에 참여 할 수 있고, 기능추가나 편집등에 제한 사항 없이 자유롭게 수정 및 업로드 하셔도 좋습니다**
**다만 타인이 수정 하거나, 추가 한 부분을 삭제하거나 수정 할때는 반드시 협의를 거쳐서 진행 해 주시길 부탁 드립니다**
**서버키는 요청 시, 공유 드릴 예정이지만, 혼선 막기 위해 가능하면 메인 관리자를 통해 merge 및 서버 업로드 요청 부탁 드립니다.**


**깃허브 처음 할때**
1. 깃허브 가입 https://github.com/

2. 깃허브 설치 https://git-scm.com/downloads

3. 깃허브 config
git config --global user.name "본인이름"
git config --global user.email "내이메일@example.com"

4. 깃허브에서 내려받기
git clone https://github.com/pradas7777/aix_study.git

5. 깃허브에 올리기 
    1) branch 생성 git checkout -b branch (<-branch에 원하는 이름>) // (https://github.com/pradas7777)에서 new branch 하셔도 됩니다
    2) 코드수정
    3) git add .
    4) git commit -m "무슨무슨 기능 추가"
    5) git push -u origin branch (아까만든 branch 이름) <<<처음에만 -u orgin branch 하시면 됩니다. 그 뒤로는 git push 만 하셔도 됩니다

6. 자기가 올린 branch에서 pull request 보내기 
    저한테 리퀘스트 보내시면 제가 메인으로 합쳐서 서버에 업로드합니다

7. main이 새로 업데이트 될때마다 git pull 해서 프로젝트 파일 최신으로 업데이트 해 주세용
    안그러면 구버전으로 로컬에서 수정해서 올리게 되면 병합할때 많이 꼬일 수도 있습니다

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
1. 핵심 게시판 5개 (수업 요약(summary), 질문 답변(qna), 정보공유 게시판(lounge),그룹스터디(),예습게시판(preview),그룹스터디(studies))
    서브 게시판 2개 (홈페이지 업데이트 내역(updates), 홈페이지 기능건의 (suggestion)) 

    -> 게시물 post로 관리 

                            이미지는 최대 5장까지 하기위해 따로 post_images, 
                            파일은 post_files 
                            댓글은 comments 
                            투표는 PollOption(투표옵션) / vote (투표), (*voter는 로그인없이 중복방지 투표를 위한 투표자 리스트 비교용)
                            조회수는 views
                            
2. 데이터 베이스는 mysql에서 생성 community_db 

# 프로젝트 구조
```
anonymous_board/
├── database.py       # MySQL 연결 설정 
├── models.py         # SQLAlchemy 데이터베이스 모델 정의 (Visitor, Post, Comment 등등)
├── main.py           # FastAPI 애플리케이션, 라우트, API 로직 등등등 ....
├── requirements.txt  # Python 에서 필요한 설치 목록
├── static/
│   └── style.css     # CSS 스타일 
└── templates/
    ├── _views.html   # 조회수
    ├── base.html     # 기본 레이아웃 및 네비게이션
    ├── index.html    # 최신 글 목록
    ├── board.html    # 새 글 작성 
    └── detail.html   # 글 볼때 
    └── edit.html     # 글 수정할때 보는 폼 
    └── list.html     # 글 목록 화면 
    └── detail.html   # 조회수 화면
```


# 설치 및 실행 방법
```
1. git clone 해서 프로젝트 받기

2. 필수 설치파일 설치하기 
pip install fastapi uvicorn sqlalchemy pymysql jinja2 python-multipart

3. db 생성
저희 프로젝트에 맞는 로컬 db를 생성해야합니다 
MYSQL로 접속하신 후 (본인 아이디나 루트 계정 그대로 쓰셔도 되고 이 디비를 위한 계정 만드셔도 되고 상관없습니다)

mysql에서 
CREATE DATABASE community_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
community_db라는 db 만드시면 됩니닷

4. DB 연결
방금 만드신 mysql 아이디랑 비번으로 프로젝트 폴더 안에 있는 database.py 라는 파일에서 

여기를 
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://aix:1234tlsfla@localhost:3306/community_db?charset=utf8mb4"

mysql+pymysql://사용자:비밀번호@localhost:3306/community_db?charset=utf8mb4"
본인 mysql 사용자:비밀번호 로 바꿔서 저장해놓으시면됩니다

5. 그리고 프로젝트 폴더에서
uvicorn main:app --reload
치시면 http://127.0.0.1:8000으로 로컬 서버 사이트가 열립니다

6. 한번 로컬로 들어가보셨으면 아까만든 db에 테이블들이 자동생성되셨을겁니다 다만 
투표에 들어가는 실명 명단은 한번 수동으로 넣으셔야합니다. 

한번 들어가셔서 테이블이 생성되었다면 mysql에서 아래 명령어 입력하시면됩니닷

ALTER TABLE posts ADD COLUMN has_poll TINYINT(1) NOT NULL DEFAULT 0;
INSERT INTO voter (realname) VALUES
('이다빈'),
('조중하'),
('이동원'),
('최윤성'),
('윤기혁'),
('이혜영'),
('최경섭'),
('김동수'),
('채진용'),
('신건식'),
('김현봉'),
('조민성'),
('이가연'),
('이은아'),
('김민정'),
('전명준'),
('하만석'),
('김지수');
```