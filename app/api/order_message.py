from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.order_message.crud import (
    create_order_message,
    get_order_message_by_order_id,
    delete_order_message_by_id,
    modify_order_message_by_id
)

from app.models.schemas.order_message import (
    OrderMessageCreateModel,
    OrderMessageViewModel,
    OrderMessageModifyModel
)
router = APIRouter()


# 新增工單訊息
@router.post("/order_message", response_model=OrderMessageViewModel)
def create_a_order_message(order_message_create: OrderMessageCreateModel, user_id: int,
                           Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)
    reporter_user_id = current_user.id if current_user.level != 0 else user_id
    if current_user.level > 2:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return create_order_message(db, reporter_user_id, order_message_create)


# 取得工單訊息 (RD)
@router.get("/order_message", response_model=List[OrderMessageViewModel])
def get_order(order_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)
    return get_order_message_by_order_id(db, order_id)


# 刪除工單訊息
@router.delete("/order_message")
def delete_order(issue_id, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level > 2:
        raise HTTPException(status_code=401, detail="Unauthorized")
    delete_order_message_by_id(db, issue_id)


# 修改工單訊息
@router.patch("/order_message")
def modify_order_message(order_message_modify: OrderMessageModifyModel,
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level > 2:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return modify_order_message_by_id(db, order_message_modify)
