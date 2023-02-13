import pytest
from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from app.server.authentication import get_user_by_email, authorize_user, create_user
from app.server.schemas import UserCreateModel


def test_create_a_user_with_valid_user(db: Session, Authorize: AuthJWT):
    current_user = authorize_user(Authorize, db)
    user_create = UserCreateModel(email="test@example.com", level=2)
    if current_user.level >= user_create.level or current_user.level >= 2:
        with pytest.raises(HTTPException) as exception:
            user_db = create_a_user(user_create, Authorize, db)
    assert exception.value.status_code == 401
    assert exception.value.detail == "Unauthorized"

def test_create_a_user_with_existing_email(db: Session, Authorize: AuthJWT):
    current_user = authorize_user(Authorize, db)
    user_create = UserCreateModel(email=current_user.email, level=2)
    with pytest.raises(HTTPException) as exception:
        user_db = create_a_user(user_create, Authorize, db)
    assert exception.value.status_code == 400
    assert exception.value.detail == "Email already registered"

def test_create_a_user_with_invalid_level(db: Session, Authorize: AuthJWT):
    current_user = authorize_user(Authorize, db)
    user_create = UserCreateModel(email="test@example.com", level=4)
    with pytest.raises(HTTPException) as exception:
        user_db = create_a_user(user_create, Authorize, db)
    assert exception.value.status_code == 405
    assert exception.value.detail == "Method Not Allowed"