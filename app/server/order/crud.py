import os

from fastapi import HTTPException, Response
from sqlalchemy import and_
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.Error_handler import UnicornException
from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User
from app.models.domain.user_mark_order import UserMarkOrder
from app.models.schemas.order import OrderModifyModel, OrderViewModel, OrderCreateModel, OrderMarkPost


def create_order(db: Session, company_name, order_create: OrderCreateModel):
    if not db.query(User).filter(User.id == order_create.client_id).first():
        raise UnicornException(name=create_order.__name__, description='client user not found', status_code=404)
    try:
        order_create.detail = str(order_create.detail)
        db_order = Order(**order_create.dict(),
                         company_name=company_name)
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


def get_order_view_model(each_order, engineer_name, issue_name, mark):
    engineer_name = engineer_name if engineer_name else "未指派"
    issue_name = issue_name if issue_name else "未選擇問題種類"
    mark = mark if mark else False
    return OrderViewModel(
        id=each_order.id,
        company_name=each_order.company_name,
        description=each_order.description,
        detail=eval(each_order.detail),
        engineer_name=engineer_name,
        issue_name=issue_name,
        mark=mark,
        status=each_order.status,
        created_at=each_order.created_at,
        file_name=eval(each_order.file_name)
    )


def get_all_order(db: Session, level, user_id, start_time, end_time):
    order_db = db.query(Order, User.name, OrderIssue.name, UserMarkOrder.mark).outerjoin(
        User, Order.engineer_id == User.id
    ).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id
    ).outerjoin(
        UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == user_id
        )
    )

    if level == 2:
        order_db = order_db.filter(Order.engineer_id == user_id)
    if level == 3:
        order_db = order_db.filter(Order.client_id == user_id)
    if start_time:
        order_db = order_db.filter(Order.created_at > start_time)
    if end_time:
        order_db = order_db.filter(Order.created_at < end_time)

    view_models = [get_order_view_model(each_order, engineer_name, issue_name, mark)
                   for each_order, engineer_name, issue_name, mark in order_db]
    return view_models





def get_some_order(db: Session, client_id_list, engineer_id_list, order_issue_id_list, status_list):
    # Join the Order table with the User and OrderIssue tables
    order_db = db.query(Order, User.name, OrderIssue.name).outerjoin(
        User, Order.engineer_id == User.id
    ).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id
    ).outerjoin(
        UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == User.id
        )
    )

    if client_id_list:
        order_db = order_db.filter(Order.client_id.in_(client_id_list))
    if engineer_id_list:
        order_db = order_db.filter(Order.engineer_id.in_(engineer_id_list))
    if order_issue_id_list:
        order_db = order_db.filter(Order.order_issue_id.in_(order_issue_id_list))
    if status_list:
        order_db = order_db.filter(Order.status.in_(status_list))

    # Convert each order to a view model
    view_models = [get_order_view_model(each_order, engineer_name, issue_name)
                   for each_order, engineer_name, issue_name in order_db]

    return view_models


def check_order_status(db: Session, order_id_list):
    return db.query(Order).filter(Order.id.in_(order_id_list), Order.status != 0).first()


def delete_order_by_id(db: Session, order_id_list):
    try:
        # delete all message in order
        from app.models.domain.order_message import OrderMessage
        db.query(OrderMessage).filter(OrderMessage.order_id.in_(order_id_list)).delete(synchronize_session=False)

        # delete all mark in order
        from app.models.domain.user_mark_order import UserMarkOrder
        db.query(UserMarkOrder).filter(UserMarkOrder.order_id.in_(order_id_list)).delete(synchronize_session=False)

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
            name=modify_order_principal_engineer_by_id.__name__,
            description='order not found',
            status_code=404)
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


def modify_order_principal_engineer_by_id(db: Session, order_id: int, engineer_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_principal_engineer_by_id.__name__,
            description='order not found',
            status_code=404)

    status = 1 if order_db.status == 0 else order_db.status
    order_db.engineer_id = engineer_id
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


def order_mark_by_user(db: Session, user_id, order_mark: OrderMarkPost):

    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnicornException(
            name=order_mark_by_user.__name__,
            description='User does not exist',
            status_code=404)

    # Check if the order exists
    order = db.query(Order).filter(Order.id == order_mark.order_id).first()
    if not order:
        raise UnicornException(
            name=order_mark_by_user.__name__,
            description='Order does not exist',
            status_code=404)

    # Check if the user has marked the order
    mark_db = db.query(UserMarkOrder).filter(
            UserMarkOrder.user_id == user_id,
            UserMarkOrder.order_id == order_mark.order_id
        ).first()

    try:
        # If the mark is empty, delete the mark from the database
        if not order_mark.mark:
            if mark_db:
                db.delete(mark_db)
                db.commit()

        # If the mark is not empty, and the mark does not exist in the database, add it to the database
        else:
            if not mark_db:
                mark = UserMarkOrder(**order_mark.dict(), user_id=user_id)
                db.add(mark)
                db.commit()
                db.refresh(mark)
    except Exception as e:
        print(str(e))
        raise UnicornException(name=delete_order_by_id.__name__, description=str(e), status_code=500)

    return "Done"


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
