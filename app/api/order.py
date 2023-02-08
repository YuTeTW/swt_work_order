from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.order.crud import (
    create_order,
    get_all_order,
    get_some_order,
    delete_order_by_id,
    check_order_status,
    modify_order_by_id,
    modify_order_status_by_id,
    modify_order_principal_engineer_by_id,
    check_modify_status_permission,
    upload_picture_to_folder,
    download_picture_from_folder,
    delete_picture_from_folder
)

from app.models.schemas.order import (
    OrderCreateModel,
    OrderCreateResponseModel,
    OrderFilterBodyModel,
    OrderDeleteIdModel,
    OrderModifyModel
)
from app.server.send_email import send_email
from app.server.user.crud import (
    get_user_by_id
)
router = APIRouter()


# 新增工單
# @router.post("/order",)
@router.post("/order", response_model=OrderCreateResponseModel)
async def create_a_order(order_create: OrderCreateModel, background_tasks: BackgroundTasks, client_id: int = 1,
                         Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)
    user_db = get_user_by_id(db, client_id)
    if current_user.level < 3 and current_user.id == client_id:
        raise HTTPException(status_code=422, detail="Only create order for client")
    if current_user.level == 3 and user_db.id != client_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    order_db = create_order(db, user_db.id, user_db.name, order_create)

    # 建單後寄信
    # send_email("judhaha@gmail.com", background_tasks)
    return order_db


# 取得所有order (pm)
@router.get("/order/all")
def get_order(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level > 1:
        raise HTTPException(status_code=401, detail="Unauthorized")
    all_order = get_all_order(db)
    return all_order


# 取得部分order (RD)
@router.get("/order")
def get_some_orders(filter_body: OrderFilterBodyModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level > 1 and filter_body.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if current_user.level > 1 and filter_body.engineer_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_some_order(
        db, filter_body.user_id, filter_body.engineer_id, filter_body.order_issue_id, filter_body.status
    )


# 刪除工單
@router.delete("/order")
def delete_order(order_id: OrderDeleteIdModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level == 2:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if current_user.level == 3 and check_order_status(db, order_id.order_id_list):
        raise HTTPException(status_code=400, detail="One of orders is already in progress")
    return delete_order_by_id(db, order_id.order_id_list)


# 修改工單資訊
@router.patch("/order")
def modify_order(order_modify_body: OrderModifyModel,
                 db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level == 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level == 3 and check_order_status(db, [order_modify_body.order_id]):
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
    if current_user.level == 3:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level == 2 and current_user.id != engineer_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return modify_order_principal_engineer_by_id(db, order_id, engineer_id)


# 上傳照片
@router.post("/order/picture")
async def upload_picture(order_id: int, file: UploadFile,
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level in (1, 2):
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
async def download_picture(order_id: int, file_name: str,
                           db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)
    return delete_picture_from_folder(db, order_id, file_name)
