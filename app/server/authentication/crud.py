from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import User
from app.server.authentication import create_random_password
from app.server.user.crud import get_password_hash


def check_user_email_enable(db: Session, user_email: str):
    user_db = db.query(User).filter(User.email == user_email).first()
    if user_db.is_enable:
        raise HTTPException(status_code=202, detail="user 已啟用了")


def set_user_enable(db: Session, user_email: str):
    user_db = db.query(User).filter(User.email == user_email).first()
    db.begin()
    try:
        user_db.is_enable = True
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=set_user_enable.__name__, description=str(e), status_code=500)
    return user_db


def create_and_set_user_password(db: Session, user_email: str):
    user_db = db.query(User).filter(User.email == user_email).first()
    password = create_random_password()
    hashed_password = get_password_hash(password)
    db.begin()
    try:
        user_db.password = hashed_password
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_and_set_user_password.__name__, description=str(e), status_code=500)
    return password
