import random
from datetime import timedelta, datetime
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from enum import Enum

from app.db.database import get_db
from app.models.domain.user import User


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60 * 60 * 1000  # 一天
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
default_user_setting_options = {"settings": "settings"}

verify_code_token = []

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class AuthorityLevel(Enum):
    root = 0
    admin = 1
    engineer = 2
    client = 3


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.name == username).first()


def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    if not user.is_enable:
        raise HTTPException(status_code=401, detail="user 尚未啟用")
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


def get_email_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["email"] is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload


def check_level(current_user: User, level):
    if current_user.level == -1:
        raise HTTPException(status_code=403, detail="你還沒設定角色權限")

    if current_user.level > level:
        return False
    return True


def create_random_password():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


def create_random_verify_code():
    seed = "1234567890"
    sa = []
    for i in range(4):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


def save_verify_code_to_token(verify_code: str, email: str, expires_delta: Optional[timedelta] = None):
    to_encode = {"verify_code": verify_code,
                 "email": email}
    if expires_delta:
        expire = datetime.utcnow() + expires_dwelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    verify_code_token.append(encoded_jwt)
    return encoded_jwt


def check_verify_code(verify_code: str, email: str):
    for token in verify_code_token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            eatch_verify_code: str = payload.get("verify_code")
            eatch_verify_email: str = payload.get("email")
            if eatch_verify_code is None:
                verify_code_token.remove(eatch_verify_code)

        except JWTError:
            raise credentials_exception

        if eatch_verify_code == verify_code and eatch_verify_email == email:
            verify_code_token.remove(token)
            return True

    return False
