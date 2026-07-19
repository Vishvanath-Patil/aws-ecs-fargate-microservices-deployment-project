import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, UniqueConstraint, create_engine, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./likes.db")
SECRET_KEY = os.getenv("JWT_SECRET", "devconnect-local-secret")
ALGORITHM = "HS256"
API_PREFIX = os.getenv("API_PREFIX", "/api/like")

#engine = create_engine(DATABASE_URL, pool_pre_ping=True)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
bearer = HTTPBearer()


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="unique_post_user_like"),)

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LikeRequest(BaseModel):
    post_id: int

app = FastAPI(title="DevConnect Like Service")


@app.middleware("http")
async def strip_api_prefix(request, call_next):
    if API_PREFIX and request.scope["path"].startswith(API_PREFIX):
        request.scope["path"] = request.scope["path"][len(API_PREFIX) :] or "/"
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def identity(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "like"}


@app.get("/likes")
def like_counts(db: Session = Depends(db_session)):
    rows = db.query(Like.post_id, func.count(Like.id)).group_by(Like.post_id).all()
    return {str(post_id): count for post_id, count in rows}


@app.post("/likes/toggle")
def toggle_like(payload: LikeRequest, claims=Depends(identity), db: Session = Depends(db_session)):
    like = db.query(Like).filter(Like.post_id == payload.post_id, Like.user_id == claims["user_id"]).first()
    liked = False
    if like:
        db.delete(like)
    else:
        db.add(Like(post_id=payload.post_id, user_id=claims["user_id"]))
        liked = True
    db.commit()
    count = db.query(func.count(Like.id)).filter(Like.post_id == payload.post_id).scalar()
    return {"post_id": payload.post_id, "liked": liked, "count": count}
