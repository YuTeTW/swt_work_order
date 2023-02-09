from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import User
from app.server.authentication import create_random_password
from app.server.user.crud import get_password_hash


def set_user_enable(db: Session, user_id: int, is_enable: bool):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnicornException(name=set_user_enable.__name__,
                               description='User not found', status_code=404)
    user.is_enable = is_enable
    user.updated_at = datetime.now()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=set_user_enable.__name__,
                               description=str(e), status_code=500)


def create_and_set_user_password(db: Session, user_email: str):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise UnicornException(name=create_and_set_user_password.__name__,
                               description='User not found', status_code=404)
    password = create_random_password()
    hashed_password = get_password_hash(password)
    user.password = hashed_password
    user.updated_at = datetime.now()
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=create_and_set_user_password.__name__,
                               description=str(e), status_code=500)
