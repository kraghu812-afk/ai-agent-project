import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

# Load local development settings from .env. Never commit the real .env file.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "users.db"

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "replace-this-with-a-random-secret":
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Create a .env file and set a strong random key. "
        "See README.md."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI(
    title="Raghu AI Agent API",
    description="A beginner-friendly AI Agent API with JWT authentication.",
    version="2.0.0",
)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    username: str
    reply: str


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()


def create_access_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserPublic:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            raise credentials_error
    except InvalidTokenError:
        raise credentials_error

    # Check that the account still exists; a deleted account cannot keep using a token.
    with get_connection() as connection:
        user = connection.execute(
            "SELECT username FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if user is None:
        raise credentials_error

    return UserPublic(username=user["username"])


@app.get("/")
def home():
    return {"message": "Welcome to Raghu AI Agent API", "docs": "/docs"}


@app.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate):
    hashed_password = password_hash.hash(user_data.password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    user_data.username,
                    hashed_password,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already registered.",
        )

    return UserPublic(username=user_data.username)


@app.post("/auth/token", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT username, password_hash
            FROM users
            WHERE username = ? COLLATE NOCASE
            """,
            (form_data.username,),
        ).fetchone()

    # Use the same error for an unknown username and a wrong password.
    if user is None or not password_hash.verify(
        form_data.password,
        user["password_hash"] if user else password_hash.hash("invalid-password"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user["username"])
    return TokenResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@app.get("/users/me", response_model=UserPublic)
def read_current_user(
    current_user: Annotated[UserPublic, Depends(get_current_user)],
):
    return current_user


@app.post("/agent/chat", response_model=ChatResponse)
def chat_with_agent(
    request: ChatRequest,
    current_user: Annotated[UserPublic, Depends(get_current_user)],
):
    message = request.message.strip()
    normalized = message.lower()

    if normalized == "hello":
        reply = f"Hello {current_user.username}! How can I help you?"
    elif normalized == "help":
        reply = "I can respond to hello, help, and bye. More AI features are coming."
    elif normalized == "bye":
        reply = "Goodbye! Have a great day."
    else:
        reply = "I am learning. Try: hello, help, or bye."

    return ChatResponse(username=current_user.username, reply=reply)
