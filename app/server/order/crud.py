import os

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.domain.Error_handler import UnicornException
from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User
from app.models.schemas.order import OrderModifyModel, OrderViewModel, OrderCreateModel


def create_order(db: Session, company_name, order_create: OrderCreateModel):
    if not db.query(User).filter(User.id == order_create.client_id).first():
        raise UnicornException(name=create_order.__name__, description='client user not found', status_code=404)
    try:
        db_order = Order(order_issue_id=order_create.order_issue_id,
                         serial_number=order_create.serial_number,
                         description=order_create.description,
                         detail=str(order_create.detail),
                         client_id=order_create.client_id,
                         company_name=company_name,
                         )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        db_order.detail = eval(db_order.detail)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
        db_order.file_name = eval(db_order.file_name)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_order.__name__, description=str(e), status_code=500)
    return db_order


def get_order_by_user_id(db: Session, user_id):
    order_db = db.query(Order).filter(Order.client_id == user_id).first()
    return order_db


def get_all_order(db: Session):
    order_list = list()
    order_db = db.query(Order, User.name, OrderIssue.name).outerjoin(User, Order.engineer_id == User.id).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id).all()
    for each_order, engineer_name, issue_name in order_db:
        engineer_name = engineer_name if engineer_name else "未指派"
        issue_name = issue_name if issue_name else "未選擇問題種類"
        order = OrderViewModel(
            company_name=each_order.company_name,
            serial_number=each_order.serial_number,
            description=each_order.description,
            detail=eval(each_order.detail),
            engineer_name=engineer_name,
            issue_name=issue_name,
            mark=each_order.mark,
            status=each_order.status,
            created_at=each_order.created_at,
            file_name=eval(each_order.file_name)
        )
        order_list.append(order)
    return order_list

    # plan B 用pandas
    # import pandas as pd
    #
    # order_db = db.query(Order, User.name, OrderIssue.name).outerjoin(User, Order.engineer_id == User.id).outerjoin(
    #     OrderIssue, Order.order_issue_id == OrderIssue.id).all()
    #
    # df = pd.DataFrame(order_db, columns=['Order', 'engineer_name', 'issue_name'])
    # df['engineer_name'] = df['engineer_name'].fillna("未指派")



def get_some_order(db: Session, user_id_list=None, engineer_id_list=None, order_issue_id_list=None, status_list=None):
    order_db = db.query(Order, User.name, OrderIssue.name).filter(
        Order.engineer_id == User.id, Order.order_issue_id == OrderIssue.id).filter(
        Order.client_id.in_(user_id_list), Order.engineer_id.in_(engineer_id_list),
        Order.order_issue_id.in_(order_issue_id_list), Order.status.in_(status_list))
    order_list = []
    for each_order, engineer_name, issue_name in order_db:
        order_list.append(
            OrderViewModel(
                company_name=each_order.company_name,
                serial_number=each_order.serial_number,
                description=each_order.description,
                detail=eval(each_order.detail),
                engineer_name=engineer_name or "未派发",
                issue_name=issue_name,
                mark=each_order.mark,
                status=each_order.status,
                created_at=each_order.created_at,
                file_name=eval(each_order.file_name)
            )
        )

    return order_list


def check_order_status(db: Session, order_id_list):
    return db.query(Order).filter(and_(Order.id.in_(order_id_list), Order.status != 0)).first()


def delete_order_by_id(db: Session, order_id_list):
    try:
        from app.models.domain.order_message import OrderMessage
        db.query(OrderMessage).filter(OrderMessage.order_id.in_(order_id_list)).delete(synchronize_session=False)
        db.query(Order).filter(Order.id.in_(order_id_list)).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=delete_order_by_id.__name__, description=str(e), status_code=500)
    # 刪除圖片
    for order_id in order_id_list:
        file_path = os.getcwd() + "/db_image/order_pic_name_by_id/" + str(order_id) + ".jpg"
        if os.path.exists(file_path):
            os.remove(file_path)
    return "Order deleted successfully"


def modify_order_by_id(db: Session, order_modify: OrderModifyModel):
    order_db = db.query(Order).filter(Order.id == order_modify.order_id)
    if not order_db.first():
        raise UnicornException(name=modify_order_by_id.__name__, description='order not found', status_code=404)
    order_db.order_issue_id = order_modify.order_issue_id
    order_db.serial_number = order_modify.serial_number
    order_db.description = order_modify.description
    order_db.detail = order_modify.detail
    order_db.updated_at = datetime.now()
    db.commit()
    return order_db


def check_modify_status_permission(current_user, now_status, status):
    if current_user.level == 3:  # client
        if now_status != 2 or status not in [1, 3]:
            raise HTTPException(status_code=401, detail="Unauthorized")
    elif current_user.level == 2:  # engineer
        if status in [3, 0]:
            raise HTTPException(status_code=401, detail="Unauthorized")
    elif current_user.level == 1:  # pm
        if status == 3:
            raise HTTPException(status_code=401, detail="Unauthorized")


def modify_order_status_by_id(db: Session, order_id: int, status: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_principal_engineer_by_id.__name__, description='order not found', status_code=404)
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


def modify_order_principal_engineer_by_id(db: Session, order_id: int, engineer_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_principal_engineer_by_id.__name__, description='order not found', status_code=404)

    status = 1 if order_db.status == 0 else order_db.status
    order_db.engineer_id = engineer_id
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


async def upload_picture_to_folder(db: Session, order_id, picture_file):
    file_dir = os.path.join(os.getcwd(), "db_image/order_pic_name_by_id/")
    os.makedirs(file_dir, exist_ok=True)
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    try:
        file_names = eval(order.file_name)
        if picture_file.filename not in file_names:
            file_names.append(picture_file.filename)
            order.file_name = str(file_names)
            order.updated_at = datetime.now()
            db.commit()
        file_path = os.path.join(file_dir, picture_file.filename)
        with open(file_path, "wb") as f:
            f.write(await picture_file.read())
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Failed to upload image")
    return {"message": "Image uploaded successfully"}


def download_picture_from_folder(order_id):
    file_path = os.getcwd() + "/db_image/order_pic_name_by_id/" + str(order_id) + ".jpg"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image doesn't exist.")
    try:
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
            return Response(content=image_data, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to download image")


def delete_picture_from_folder(db: Session, order_id, file_name):
    file_path = os.getcwd() + "/db_image/order_pic_name_by_id/" + str(file_name)
    order = db.query(Order).filter_by(id=order_id).first()
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image doesn't exist.")
    else:
        try:
            os.remove(file_path)
            file_names = eval(order.file_name)
            if file_name in file_names:
                file_names.remove(file_name)
                order.file_name = str(file_names)
                order.updated_at = datetime.now()
                db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to Delete image")
    return "Image deleted successfully"
