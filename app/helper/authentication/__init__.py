from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from app.server.authentication import get_user_by_email


def authorize_user(Authorize: AuthJWT, db: Session):
    Authorize.jwt_required()
    current_user_email = Authorize.get_jwt_subject()
    current_user = get_user_by_email(current_user_email, db)
    if not current_user and current_user_email:
        raise HTTPException(status_code=404, detail="please Login again")
    return current_user
