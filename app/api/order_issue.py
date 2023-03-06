from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel
from app.server.order_issue.crud import (
    create_order_issue,
    get_all_order_issue,
    delete_order_issue_by_id,
    modify_order_issue_by_id
)

from app.models.schemas.order_issue import (
    OrderIssueCreateModel,
    OrderIssueViewModel,
    OrderIssueModifyModel
)
router = APIRouter()


# 新增工單類別
@router.post("/order_issue", response_model=OrderIssueViewModel)
def create_a_order_issue(order_issue_create: OrderIssueCreateModel,
                         Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.engineer.value:
        raise HTTPException(status_code=401, detail="Unauthorized")


    print(order_issue_create.time_hours)
    return create_order_issue(db, order_issue_create)


# 取得所有工單類別
@router.get("/order_issue", response_model=List[OrderIssueViewModel])
def get_order(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)

    return get_all_order_issue(db)


# 刪除工單類別
@router.delete("/order_issue")
def delete_order(issue_id, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.pm.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    delete_order_issue_by_id(db, issue_id)


# 修改工單類別
@router.patch("/order_issue", response_model=OrderIssueViewModel)
def modify_order_issue(order_issue_modify: OrderIssueModifyModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.pm.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return modify_order_issue_by_id(db, order_issue_modify)
