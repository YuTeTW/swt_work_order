from datetime import datetime
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import User
from app.models.schemas.user import UserPatchPasswordViewModel, UserCreateModel, UserPatchInfoModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    user_db = db.query(User).filter(User.id == user_id).first()
    return user_db


def check_user_exist(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def check_root_exist(db):
    return db.query(User).filter(User.level == 0).first()


def modify_user(db: Session, user_patch: UserPatchInfoModel):
    user_db = db.query(User).filter(User.id == user_patch.user_id).first()
    try:
        user_db_info = user_db.info.copy()
        user_db.level = user_patch.level
        user_db.name = user_patch.name
        user_db_info["contact_email"] = user_patch.contact_email
        user_db_info["telephone_number"] = user_patch.telephone_number
        user_db_info["line"] = user_patch.line
        user_db.info = user_db_info
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_user.__name__, description=str(e), status_code=500)
    return user_db


def modify_user_password(db: Session, user_id: int, userPatch: UserPatchPasswordViewModel):
    user_db = db.query(User).filter(User.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    try:
        hashed_password = get_password_hash(userPatch.new_password)
        user_db.password = hashed_password
        user_db.updated_at = datetime.now()
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_user_password.__name__, description=str(e), status_code=500)
    return user_db


def check_email_exist(db: Session, email: str):
    user_db = db.query(User).filter(User.email == email).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="Email does not exist")
    return user_db


def update_user_status(db: Session, user_id: int, status: bool):
    user_db = db.query(User).filter(User.id == user_id).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="user not exist")
    db.begin()
    try:
        user_db.is_enable = status
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=update_user_status.__name__, description=str(e), status_code=500)
    return user_db


def create_user(db: Session, user_create: UserCreateModel):
    try:
        hashed_password = get_password_hash(user_create.password)
        user_create.password = hashed_password
        db_user = User(**user_create.dict(), is_enable=True)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_user.__name__, description=str(e), status_code=500)
    return db_user


def check_User_Exist(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user is not exist")
    return db_user



def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def change_user_level(db: Session, user_id: int, level: int):
    user_db = db.query(User).filter(User.id == user_id).first()
    if level < 2 or level > 4:
        raise UnicornException(name=change_user_level.__name__, description="權限 level 請輸入 2~4", status_code=400)
    db.begin()
    try:
        user_db.level = level
        user_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=change_user_level.__name__, description=str(e), status_code=500)
    return user_db


def delete_user_by_user_id(db: Session, user_id: int):
    try:
        user_db = db.query(User).filter(User.id == user_id).first()
        db.delete(user_db)
        db.commit()
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=delete_user_by_user_id.__name__, description=str(e), status_code=500)
    return "User deleted successfully"

