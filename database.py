from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 연결 설정
# 형식: mysql+pymysql://사용자:비밀번호@호스트:포트/데이터베이스명?charset=utf8mb4
# 로컬 환경에 맞게 수정이 필요할 수 있습니다.
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://aix:1234tlsfla@localhost:3306/community_db?charset=utf8mb4"

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # MySQL 연결 유지 및 타임아웃 방지 설정
    pool_recycle=3600,
    pool_pre_ping=True
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 베이스 클래스
Base = declarative_base()

# DB 세션 의존성 주입을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
