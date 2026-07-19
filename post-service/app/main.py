import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./posts.db")
SECRET_KEY = os.getenv("JWT_SECRET", "devconnect-local-secret")
ALGORITHM = "HS256"
API_PREFIX = os.getenv("API_PREFIX", "/api/post")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
bearer = HTTPBearer()


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False, index=True)
    body = Column(Text, nullable=False)
    tag = Column(String(40), default="General")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PostRequest(BaseModel):
    body: str = Field(min_length=3, max_length=500)
    tag: str = Field(default="General", max_length=40)


app = FastAPI(title="DevConnect Post Service")


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


def serialize(post: Post):
    return {
        "id": post.id,
        "user_id": post.user_id,
        "username": post.username,
        "body": post.body,
        "tag": post.tag,
        "created_at": post.created_at.isoformat(),
    }


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "post"}


@app.get("/posts")
def posts(db: Session = Depends(db_session)):
    rows = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
    return [serialize(row) for row in rows]


@app.post("/posts")
def create_post(payload: PostRequest, claims=Depends(identity), db: Session = Depends(db_session)):
    post = Post(user_id=claims["user_id"], username=claims["sub"], body=payload.body, tag=payload.tag or "General")
    db.add(post)
    db.commit()
    db.refresh(post)
    return serialize(post)


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, claims=Depends(identity), db: Session = Depends(db_session)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != claims["user_id"]:
        raise HTTPException(status_code=403, detail="You can delete only your posts")
    db.delete(post)
    db.commit()
    return {"deleted": post_id}
