import os
import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auth.db")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("JWT_SECRET", "devconnect-local-secret")
ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("TOKEN_MINUTES", "1440"))
API_PREFIX = os.getenv("API_PREFIX", "/api/auth")

#engine = create_engine(DATABASE_URL, pool_pre_ping=True)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/login")
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=120)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


app = FastAPI(title="DevConnect Auth Service")


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(user: AuthUser) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    payload = {"sub": user.username, "user_id": user.id, "email": user.email, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> AuthUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    user = db.query(AuthUser).filter(AuthUser.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# @app.get("/health")
# def health():
#     return {"status": "ok", "service": "auth"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "service": "auth"}
    except Exception:
        raise HTTPException(status_code=500, detail="DB not ready")


@app.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthUser(
        username=payload.username.strip().lower(),
        email=payload.email.strip().lower(),
        hashed_password=pwd_context.hash(payload.password),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists") from exc
    token = create_token(user)
    return {"access_token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AuthUser).filter(AuthUser.username == payload.username.strip().lower()).first()
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user)
    return {"access_token": token, "user": {"id": user.id, "username": user.username, "email": user.email}}


@app.get("/me")
def me(user: AuthUser = Depends(current_user)):
    return {"id": user.id, "username": user.username, "email": user.email}
