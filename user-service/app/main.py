import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
SECRET_KEY = os.getenv("JWT_SECRET", "devconnect-local-secret")
ALGORITHM = "HS256"
API_PREFIX = os.getenv("API_PREFIX", "/api/user")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
bearer = HTTPBearer()


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    display_name = Column(String(80), nullable=False)
    title = Column(String(120), default="Cloud builder")
    location = Column(String(100), default="Remote")
    bio = Column(Text, default="")
    avatar_color = Column(String(20), default="#14b8a6")
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ProfileRequest(BaseModel):
    display_name: str = Field(min_length=2, max_length=80)
    title: str = Field(max_length=120)
    location: str = Field(max_length=100)
    bio: str = Field(max_length=500)
    avatar_color: str = Field(default="#14b8a6", max_length=20)


app = FastAPI(title="DevConnect User Service")


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


def serialize(profile: Profile):
    return {
        "user_id": profile.user_id,
        "username": profile.username,
        "display_name": profile.display_name,
        "title": profile.title,
        "location": profile.location,
        "bio": profile.bio,
        "avatar_color": profile.avatar_color,
    }


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "user"}


@app.get("/profiles")
def profiles(db: Session = Depends(db_session)):
    rows = db.query(Profile).order_by(Profile.updated_at.desc()).limit(24).all()
    return [serialize(row) for row in rows]


@app.get("/profiles/me")
def my_profile(claims=Depends(identity), db: Session = Depends(db_session)):
    profile = db.get(Profile, claims["user_id"])
    if not profile:
        return {
            "user_id": claims["user_id"],
            "username": claims["sub"],
            "display_name": claims["sub"].title(),
            "title": "Cloud builder",
            "location": "Remote",
            "bio": "Designing reliable systems and useful products.",
            "avatar_color": "#14b8a6",
        }
    return serialize(profile)


@app.put("/profiles/me")
def update_profile(payload: ProfileRequest, claims=Depends(identity), db: Session = Depends(db_session)):
    profile = db.get(Profile, claims["user_id"])
    if not profile:
        profile = Profile(user_id=claims["user_id"], username=claims["sub"])
        db.add(profile)
    profile.display_name = payload.display_name
    profile.title = payload.title
    profile.location = payload.location
    profile.bio = payload.bio
    profile.avatar_color = payload.avatar_color
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return serialize(profile)
