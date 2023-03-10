from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel
from app.server.order import OrderStatus
from app.server.order.crud_file import (
    upload_picture_to_folder,
    download_picture_from_folder,
    delete_picture_from_folder,
)
from app.server.order.crud import (
    create_order,
    get_all_order,
    delete_order_by_id,
    check_order_status,
    modify_order_by_id,
    modify_order_status_by_id,
    modify_order_principal_engineer_by_id,
    order_mark_by_user,
    check_modify_status_permission,
    get_a_order,
    get_order_status, get_order_engineer_id, get_order_reporter, test_get_all_order,
    modify_order_status_and_add_solution_by_id,
)

from app.models.schemas.order import (
    OrderCreateModel,
    OrderCreateResponseModel,
    OrderDeleteIdModel,
    OrderModifyModel,
    OrderViewModel,
    OrderMarkPost
)
# from app.server.send_email import send_email
from app.server.order.output_pdf import get_report
from app.server.order_message.crud import (
    create_message_cause_engineer,
    create_message_cause_status, create_message_cause_order_info, create_message_cause_file,
    create_message_cause_status_and_solution
)
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

    # check order create for client
    if current_user.level < AuthorityLevel.client.value and current_user.id == order_create.client_id:
        raise HTTPException(status_code=422, detail="Only create order for client")

    # check client can't create order for other client
    if current_user.level == AuthorityLevel.client.value and current_user.id != order_create.client_id:
        raise HTTPException(status_code=401, detail="Client only create order for self")

    if order_create.report_time:
        order_create.report_time = datetime.strptime(order_create.report_time, "%Y-%m-%d")
    order_db = create_order(db, current_user.id, user_db.name, order_create)

    # Send email after create new order
    # send_email("judhaha@gmail.com", background_tasks)
    return order_db


# 取得所有工單
# @router.get("/order/all", response_model=List[OrderViewModel])
@router.get("/order/all")
def get_all_orders(start_time: Optional[str] = None, end_time: Optional[str] = None,
                   db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # check the type of time filter and the time priority
    try:
        if start_time is not None:
            start_time = datetime.strptime(start_time, "%Y-%m-%d")
        if end_time is not None:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
            end_time = end_time + timedelta(days=1)
        if start_time is not None and end_time is not None and start_time > end_time:
            start_time, end_time = end_time, start_time
            end_time = end_time + timedelta(days=1)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=422, detail="""start_time or end_time type fail (example: 2023-01-25) """)

    return get_all_order(db, level=current_user.level, user_id=current_user.id,
                         start_time=start_time, end_time=end_time)


# 取得單一工單
@router.get("/order/single/{order_id}", response_model=OrderViewModel)
def get_a_order_by_id(order_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    return get_a_order(db, order_id, current_user.id)


# 刪除工單
@router.delete("/order")
def delete_order(order: OrderDeleteIdModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # check engineer doesn't has authorize to delete order
    for order_id in order.order_id_list:
        reporter_id = get_order_reporter(db, order_id)
        if reporter_id != current_user.id and current_user.level == AuthorityLevel.engineer.value:
            raise HTTPException(status_code=401, detail="You only can delete order which you create")

    # check client can't delete order when order is in progress
    if current_user.level == AuthorityLevel.client.value and check_order_status(db, order.order_id_list):
        raise HTTPException(status_code=400, detail="One of orders is already in progress")

    return delete_order_by_id(db, order.order_id_list)


# 修改工單資訊
@router.patch("/order")
def modify_order(order_modify_body: OrderModifyModel,
                 db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # # check engineer doesn't has authorized to modify order
    # if current_user.level == AuthorityLevel.engineer.value:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    # check client can't modify order when order is in progress
    if current_user.level == AuthorityLevel.client.value and check_order_status(db, [order_modify_body.order_id]):
        raise HTTPException(status_code=400, detail="One of orders is already in progress")

    # create message after modify order engineer
    order_modify_body.report_time = datetime.strptime(order_modify_body.report_time, "%Y-%m-%d")
    create_message_cause_order_info(db, current_user.id, order_modify_body)

    return modify_order_by_id(db, order_modify_body)


# 修改工單進行狀態
@router.patch("/order/status")
def modify_order_status(order_id: int, background_tasks: BackgroundTasks, status: int = 2,
                        db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # check order status
    now_status = get_order_status(db, order_id)

    if now_status == OrderStatus.not_appoint.value \
            and status == OrderStatus.working.value \
            and current_user.level != AuthorityLevel.pm.value:
        raise HTTPException(status_code=400, detail="Only pm can change status from not appoint to working")

    # check user authorize
    check_modify_status_permission(db, current_user.level, now_status, status, order_id, current_user.id)

    # start modify order
    modify_order_status_by_id(db, order_id, status)

    # create message after modify order status
    if now_status != status:
        create_message_cause_status(db, order_id, current_user.id, now_status, status)

    # send email when modify order
    # send_email("judhaha@gmail.com", background_tasks)
    return "Change order status finish"


@router.patch("/order/status/solution")
def modify_order_status(order_id: int, status: int, solution: str, background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    # check order status
    now_status = get_order_status(db, order_id)

    if now_status == OrderStatus.not_appoint.value \
            and status == OrderStatus.working.value \
            and current_user.level != AuthorityLevel.pm.value:
        raise HTTPException(status_code=400, detail="Only pm can change status from not appoint to working")

    # check user authorize
    check_modify_status_permission(db, current_user.level, now_status, status, order_id, current_user.id)

    # start modify order
    modify_order_status_and_add_solution_by_id(db, order_id, status, solution)

    # create message after modify order status
    if now_status != status:
        create_message_cause_status_and_solution(db, order_id, current_user.id, now_status, status, solution)

    # send email when modify order
    # send_email("judhaha@gmail.com", background_tasks)
    return "Change order status finish"


# 修改工單負責工程師
@router.patch("/order/engineer")
def modify_order_principal_engineer(order_id: int, engineer_id: int, background_tasks: BackgroundTasks,
                                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # check client doesn't have authorized to modify principal engineer
    if current_user.level == AuthorityLevel.client.value:
        raise HTTPException(status_code=401, detail="client can't change principal engineer")

    # check engineer doesn't have authorized to modify principal engineer to other engineer
    if current_user.level == AuthorityLevel.engineer.value and current_user.id != engineer_id:
        raise HTTPException(status_code=401, detail="engineer can't change principal to other engineer")

    # get now engineer id
    now_engineer_id = get_order_engineer_id(db, order_id)

    # start modify order principal
    order_db = modify_order_principal_engineer_by_id(db, order_id, engineer_id)

    # create message after modify order engineer
    if now_engineer_id != engineer_id:
        create_message_cause_engineer(db, order_id, now_engineer_id, engineer_id, current_user.id)

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

    reporter_id = get_order_reporter(db, order_id)

    # check upload picture auth
    if current_user.level in (AuthorityLevel.pm.value, AuthorityLevel.engineer.value) \
            and current_user.id != reporter_id:
        raise HTTPException(status_code=401, detail="Only order reporter and client can upload picture")

    create_message_cause_file(db, order_id, current_user.id, file.filename, "upload")

    return await upload_picture_to_folder(db, order_id, current_user.id, file)


# 下載照片
@router.get("/order/picture")
async def download_picture(order_id: int, file_name: str,
                           db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    authorize_user(Authorize, db)

    return download_picture_from_folder(order_id, file_name)


# 刪除照片
@router.delete("/order/picture")
async def delete_picture(order_id: int, file_name: str,
                         db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    delete_response = delete_picture_from_folder(db, order_id, file_name)

    create_message_cause_file(db, order_id, current_user.id, file_name, "delete")

    return delete_response


# 輸出pdf
@router.get("/order/report/{client_id}")
async def upload_picture(client_id: int, month: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.engineer.value and current_user.id != client_id:
        raise HTTPException(status_code=401, detail="only can output yourself report")

    return await get_report(db, client_id, month)


##################################################
# @router.get("/test", response_model=List[dict])
@router.get("/test")
def test_get_all_orders(start_time: Optional[str] = None, end_time: Optional[str] = None,
                        db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # create message after modify order engineer
    current_user = authorize_user(Authorize, db)
    # print(current_user.id)
    # create_message_cause_order_info(db, 9, order_modify_body)
    return test_get_all_order(db, current_user.id)

