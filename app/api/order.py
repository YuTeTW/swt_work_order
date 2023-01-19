from fastapi import APIRouter, Depends, HTTPException
from typing import List
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel, verify_password, check_level, get_email_token


router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 取得所有User (RD)
@router.get("/order")
def get_order(user_id: list,
        db: Session = Depends(get_db()), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    get_order_by_user_id(db, )


