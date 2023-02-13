from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel
from app.server.order.crud import (
    create_order,
    get_all_order,
    get_some_order,
    delete_order_by_id,
    check_order_status,
    modify_order_by_id,
    modify_order_status_by_id,
    modify_order_principal_engineer_by_id,
    order_mark_by_user,
    check_modify_status_permission,
    upload_picture_to_folder,
    download_picture_from_folder,
    delete_picture_from_folder, test_get_all_order
)

from app.models.schemas.order import (
    OrderGetFilterTimeModel,
    OrderCreateModel,
    OrderCreateResponseModel,
    OrderFilterBodyModel,
    OrderDeleteIdModel,
    OrderModifyModel,
    OrderViewModel,
    OrderMarkPost
)
# from app.server.send_email import send_email
from app.server.user.crud import (
    get_user_by_id
)
router = APIRouter()


# 新增工單
@router.post("/order", response_model=OrderCreateResponseModel)
async def create_a_order(order_create: OrderCreateModel, background_tasks: BackgroundTasks,
                         Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)
    user_db = get_user_by_id(db, order_create.client_id)

    if current_user.level < AuthorityLevel.client.value and current_user.id == order_create.client_id:
        raise HTTPException(status_code=422, detail="Only create order for client")

    if current_user.level == AuthorityLevel.client.value and current_user.id != order_create.client_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    order_db = create_order(db, user_db.name, order_create)

    # Send email after create new order
    # send_email("judhaha@gmail.com", background_tasks)
    return order_db


# 取得所有工單
@router.get("/order/all", response_model=List[OrderViewModel])
def get_all_orders(filter_time: OrderGetFilterTimeModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    return get_all_order(db, level=current_user.level, user_id=current_user.id, filter_time=filter_time)


# 取得部分工單
@router.get("/order", response_model=List[OrderViewModel])
def get_some_orders(filter_body: OrderFilterBodyModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.pm.value and filter_body.client_id_list:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level > AuthorityLevel.pm.value and filter_body.engineer_id_list:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return get_some_order(
        db, filter_body.client_id_list,
        filter_body.engineer_id_list,
        filter_body.order_issue_id_list,
        filter_body.status_list
    )


# 刪除工單
@router.delete("/order")
def delete_order(order_id: OrderDeleteIdModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level == AuthorityLevel.engineer.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level == AuthorityLevel.client.value and check_order_status(db, order_id.order_id_list):
        raise HTTPException(status_code=400, detail="One of orders is already in progress")

    return delete_order_by_id(db, order_id.order_id_list)


# 修改工單資訊
@router.patch("/order")
def modify_order(order_modify_body: OrderModifyModel,
                 db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level == AuthorityLevel.engineer.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level == AuthorityLevel.client.value and check_order_status(db, [order_modify_body.order_id]):
        raise HTTPException(status_code=400, detail="One of orders is already in progress")

    return modify_order_by_id(db, order_modify_body)


# 修改工單進行狀態
@router.patch("/order/status")
def modify_order_status(order_id: int, status: int, background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    now_status = check_order_status(db, [order_id])
    order_db = check_modify_status_permission(current_user, now_status, status)
    modify_order_status_by_id(db, order_id, status)

    # send_email("judhaha@gmail.com", background_tasks)
    return order_db


# 修改工單負責工程師
@router.patch("/order/principal")
def modify_order_principal_engineer(order_id: int, engineer_id: int, background_tasks: BackgroundTasks,
                                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level == AuthorityLevel.client.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level == AuthorityLevel.engineer.value and current_user.id != engineer_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    order_db = modify_order_principal_engineer_by_id(db, order_id, engineer_id)
    # send_email("judhaha@gmail.com", background_tasks)

    return order_db


# 修改工單記號
@router.patch("/order/mark")
def order_mark(order_mark_body: OrderMarkPost, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    return order_mark_by_user(db, current_user.id, order_mark_body)


# 上傳照片
@router.post("/order/picture")
async def upload_picture(order_id: int, file: UploadFile,
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level in (AuthorityLevel.pm.value, AuthorityLevel.engineer.value):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await upload_picture_to_folder(db, order_id, file)


# 下載照片
@router.get("/order/picture")
async def download_picture(order_id: int,
                           db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)

    return download_picture_from_folder(order_id)


# 刪除照片
@router.delete("/order/picture")
async def delete_picture(order_id: int, file_name: str,
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)

    return delete_picture_from_folder(db, order_id, file_name)



##################################################
@router.get("/test", response_model=List[OrderViewModel])
def get_all_orders(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    return test_get_all_order(db, level=current_user.level, user_id=current_user.id)
