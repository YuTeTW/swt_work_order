import os

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.domain.Error_handler import UnicornException
from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User
from app.models.schemas.order import OrderModifyModel, OrderViewModel


def create_order(db: Session, client_id, company_name, email, order_create):
    try:
        # order_db = db.query(Order).filter(Order.client_id == client_id).order_by(Order.serial_number).all()
        # db_user = Order(**order_create.dict(),
        db_order = Order(order_issue_id=order_create.order_issue_id,
                         serial_number=order_create.serial_number,
                         description=order_create.description,
                         detail=str(order_create.detail),
                         client_id=client_id,
                         status=0,
                         engineer_id=0,
                         mark=False,
                         company_name=company_name
                         )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        db_order.detail = eval(db_order.detail)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_order.__name__, description=str(e), status_code=500)
    return db_order


def get_order_by_user_id(db: Session, user_id):
    order_db = db.query(Order).filter(Order.client_id == user_id).first()
    return order_db


def get_all_order(db: Session):
    order_db = db.query(Order).all()
    # engineer_name_list = []
    # for each_order in order_db:
    #     order_dbb = db.query(User.name).filter(User.id == each_order.engineer_id).first()
    #     if order_dbb:
    #         order_dbb = order_dbb[0]
    #     engineer_name_list.append(order_dbb)
    # print(engineer_name_list)
    return order_db


def get_all_order(db: Session):
    order_db = db.query(Order).all()
    order_list = []
    for each_order in order_db:
        order_engineer = db.query(User.name).filter(User.id == each_order.engineer_id).first()
        status_name = db.query(OrderIssue.name).filter(OrderIssue.id == each_order.order_issue_id).first()
        engineer_name = order_engineer[0] if order_engineer else "未派發"
        order = OrderViewModel(
            company_name=each_order.company_name,
            serial_number=each_order.serial_number,
            description=each_order.description,
            detail=eval(each_order.detail),
            mark=each_order.mark,
            status=each_order.status,
            created_at=each_order.created_at,
            engineer_name=engineer_name,
            status_name=status_name[0]
        )
        order_list.append(order)
    return order_list


def get_some_order(db: Session, user_id_list=None, engineer_id_list=None, order_issue_id_list=None, status_list=None):
    # query = db.query(Order, User).join(User, Order.engineer_id == User.id)

    order_db = db.query(Order)
    if user_id_list:
        order_db = order_db.filter(Order.client_id.in_(user_id_list))
    if engineer_id_list:
        order_db = order_db.filter(Order.engineer_id.in_(engineer_id_list))
    if order_issue_id_list:
        order_db = order_db.filter(Order.order_issue_id.in_(order_issue_id_list))
    if status_list:
        order_db = order_db.filter(Order.status.in_(status_list))

    return order_db.all()


def check_order_status(db: Session, order_id_list):
    return db.query(Order).filter(and_(Order.id.in_(order_id_list), Order.status != 0)).first()


def delete_order_by_id(db: Session, order_id_list):
    try:
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
    order_db.update(
        {
            "order_issue_id": order_modify.order_issue_id,
            "serial_number": order_modify.serial_number,
            "description": order_modify.description,
            "detail": order_modify.detail,
            "updated_at": datetime.now()
        }
    )
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
    order_db = db.query(Order).filter(Order.id == order_id).update(
        {
            "status": status,
            "updated_at": datetime.now()
        }
    )
    return order_db


def modify_order_principal_engineer_by_id(db: Session, order_id: int, engineer_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_principal_engineer_by_id.__name__, description='order not found', status_code=404)

    status = 1 if order_db.staus == 0 else order_db.staus

    order_db = db.query(Order).filter(Order.id == order_id).update(
        {
            "engineer_id": engineer_id,
            "status": status,
            "updated_at": datetime.now()
        }
    )

    db.commit()
    return order_db


async def upload_picture_to_folder(order_id, file):
    file_path = os.getcwd() + "/db_image/order_pic_name_by_id/"
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    try:
        with open(file_path + str(order_id) + ".jpg", "wb") as f:
            f.write(await file.read())
        return {"message": "image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image")


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


def delete_picture_from_folder(order_id):
    file_path = os.getcwd() + "/db_image/order_pic_name_by_id/" + str(order_id) + ".jpg"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image doesn't exist.")
    else:
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to Delete image")
    return "Image deleted successfully"
