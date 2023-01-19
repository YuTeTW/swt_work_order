import os
import shutil
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import FILE_PATH, FASTEYES_OUTPUT_PATH
from app.models.domain.Error_handler import UnicornException, ErrorHandler

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


def clear_all_data(db: Session):
    db.begin()
    try:
        db.query(ErrorHandler).delete()

        db.query(Face).delete()
        db.query(FasteyesObservation).delete()
        db.query(FasteyesDevice).delete()
        db.query(FasteyesUuid).delete()

        db.query(Staff).delete()
        db.query(Department).delete()

        db.query(User).delete()
        db.query(Group).delete()

        if os.path.exists(FILE_PATH):
            if os.path.exists(FILE_PATH + "observation"):
                shutil.rmtree(FILE_PATH + "observation")

            if os.path.exists(FILE_PATH + "face"):
                shutil.rmtree(FILE_PATH + "face")

            if os.path.exists(FILE_PATH + "area"):
                shutil.rmtree(FILE_PATH + "area")

        if os.path.exists(FASTEYES_OUTPUT_PATH):
            shutil.rmtree(FASTEYES_OUTPUT_PATH)

        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=clear_all_data.__name__, description=str(e), status_code=500)
    return "Done"
