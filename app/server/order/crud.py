import os

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased, joinedload
from datetime import datetime, timedelta

from app.models.domain.Error_handler import UnicornException
from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User
from app.models.domain.user_mark_order import UserMarkOrder
from app.models.schemas.order import OrderModifyModel, OrderViewModel, OrderCreateModel, OrderMarkPost

from app.server.authentication import AuthorityLevel
from app.server.order import OrderStatus


def get_order_engineer_id(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    return order_db.engineer_id


def get_order_status(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise HTTPException(status_code=404, detail='order status not found')
    return order_db.status


def get_order_reporter(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    if not order_db:
        raise HTTPException(status_code=404, detail='order reporter not found')
    return order_db.reporter_id


def create_order(db: Session, reporter_id: int, company_name, order_create: OrderCreateModel):
    if not db.query(User).filter(User.id == order_create.client_id).first():
        raise HTTPException(status_code=404, detail='client user not found')

    if not db.query(OrderIssue).filter(OrderIssue.id == order_create.order_issue_id).first():
        raise HTTPException(status_code=404, detail='order issue not found')

    if not db.query(User).filter(User.id == reporter_id).first():
        raise HTTPException(status_code=404, detail='User not found')

    default_engineer = db.query(User).filter(User.level == AuthorityLevel.default_engineer.value).first()
    if not default_engineer:
        raise HTTPException(status_code=404, detail='default_engineer not found')

    try:
        order_create.detail = str(order_create.detail)
        db_order = Order(**order_create.dict(),
                         reporter_id=reporter_id,
                         engineer_id=default_engineer.id)
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


def get_order_view_model(each_order, engineer_name, client_name, issue_name, mark):
    engineer_name = engineer_name if engineer_name != "default_engineer" else "未指派"
    issue_name = issue_name if issue_name else "未選擇問題種類"
    mark = mark if mark else False
    try:
        dir_path = os.getcwd() + f"/db_image/order_pic_name_by_id/{each_order.id}"
        all_file_name = os.listdir(dir_path)
    except Exception as e:
        all_file_name = []
    return OrderViewModel(
        id=each_order.id,
        reporter_id=each_order.reporter_id,
        company_name=client_name,
        description=each_order.description,
        detail=eval(each_order.detail),
        engineer_name=engineer_name,
        issue_name=issue_name,
        mark=mark,
        status=each_order.status,
        created_at=each_order.created_at,
        updated_at=each_order.updated_at,
        file_name=all_file_name
    )


def get_all_order(db: Session, level: int, user_id: int, start_time: datetime, end_time: datetime):
    engineer_alias = aliased(User)
    client_alias = aliased(User)
    order_db_list = db.query(Order, engineer_alias.name, client_alias.name, OrderIssue.name,
                             UserMarkOrder.mark) \
        .outerjoin(engineer_alias, Order.engineer_id == engineer_alias.id) \
        .outerjoin(client_alias, Order.client_id == client_alias.id) \
        .outerjoin(OrderIssue, Order.order_issue_id == OrderIssue.id) \
        .outerjoin(UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == user_id
    ))

    if level == AuthorityLevel.engineer.value:
        default_engineer = db.query(User).filter_by(level=-1).first()
        order_db_list = order_db_list.filter(Order.engineer_id.in_([default_engineer.id, user_id]))

    # client only get self orders
    if level == AuthorityLevel.client.value:
        order_db_list = order_db_list.filter(Order.client_id == user_id)

    if start_time:  # filter start time
        order_db_list = order_db_list.filter(Order.created_at > start_time)

    if end_time:  # filter end time
        order_db_list = order_db_list.filter(Order.created_at < end_time)

    # print(order_db_list.all())

    view_models = [get_order_view_model(each_order, engineer_name, client_name, issue_name, mark)
                   for each_order, engineer_name, client_name, issue_name, mark in order_db_list]
    print(view_models)
    return view_models


def get_a_order(db, order_id, user_id):
    # Join the Order table with the User and OrderIssue tables
    engineer_alias = aliased(User)
    client_alias = aliased(User)
    order_db_list = db.query(Order, engineer_alias.name, client_alias.name, OrderIssue.name,
                             UserMarkOrder.mark) \
        .outerjoin(engineer_alias, Order.engineer_id == engineer_alias.id) \
        .outerjoin(client_alias, Order.client_id == client_alias.id) \
        .outerjoin(OrderIssue, Order.order_issue_id == OrderIssue.id) \
        .outerjoin(UserMarkOrder, and_(
        UserMarkOrder.order_id == Order.id,
        UserMarkOrder.user_id == user_id
    )).filter(Order.id == order_id)

    view_models = [get_order_view_model(each_order, engineer_name, client_name, issue_name, mark)
                   for each_order, engineer_name, client_name, issue_name, mark in order_db_list]

    return view_models[0]


def check_order_status(db: Session, order_id_list):
    order_db = db.query(Order).filter(Order.id.in_(order_id_list),
                                      Order.status != OrderStatus.not_appoint.value).first()
    if order_db:
        status = order_db.status
    else:
        status = None
    return status


def delete_order_by_id(db: Session, order_id_list: list):
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
    order_db = db.query(Order).filter(Order.id == order_modify.order_id).first()
    if not order_db:
        raise HTTPException(status_code=404, detail='order not found')
    order_db.order_issue_id = order_modify.order_issue_id
    order_db.description = order_modify.description
    order_db.detail = str(order_modify.detail)
    order_db.updated_at = datetime.now()
    db.commit()
    return "Order modify successfully"


def check_modify_status_permission(db: Session, level: int, now_status: int,
                                   status: int, order_id: int, current_user_id: int):
    # check client change status auth
    if level == AuthorityLevel.client.value:  # client
        if not db.query(Order).filter(Order.id == order_id, Order.client_id == current_user_id).first():
            raise HTTPException(
                status_code=401,
                detail="order isn't yours"
            )
        if now_status != OrderStatus.finsh.value:
            raise HTTPException(
                status_code=401,
                detail="client only can change status when order finish"
            )
        if status not in [OrderStatus.working.value, OrderStatus.close.value] and status != OrderStatus.finsh.value:
            raise HTTPException(
                status_code=401,
                detail="client only can change status to 'in process' or 'closing order' when order finish"
            )

    # check engineer change status auth
    elif level == AuthorityLevel.engineer.value:  # engineer
        if status in [OrderStatus.close.value, OrderStatus.not_appoint.value]:
            raise HTTPException(
                status_code=401,
                detail="engineer only can change status to not appoint or finish"
            )
        if status == OrderStatus.working.value and not db.query(Order).filter(
                Order.engineer_id == current_user_id).first():
            raise HTTPException(
                status_code=401,
                detail="engineer only can change principle order status"
            )
    # check pm change status auth
    elif level == AuthorityLevel.pm.value:  # pm
        order_db = db.query(Order).filter(Order.id == order_id).first()
        if status == OrderStatus.close.value and order_db.updated_at + timedelta(days=7) > datetime.now():
            raise HTTPException(
                status_code=401,
                detail="pm can't change status to close within 7 days after the order created"
            )


def modify_order_status_by_id(db: Session, order_id: int, status: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()

    if not order_db:
        raise HTTPException(status_code=404, detail="order not found")

    # status
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


def modify_order_principal_engineer_by_id(db: Session, order_id: int, engineer_id: int):
    order_db = db.query(Order).filter(Order.id == order_id, Order.id == order_id).first()
    user_db = db.query(User).filter(User.id == engineer_id).first()

    if not order_db:
        raise HTTPException(status_code=404, detail="order not found")
    if not user_db:
        raise HTTPException(status_code=404, detail="user not found")

    status = OrderStatus.working.value if order_db.status == OrderStatus.not_appoint.value else order_db.status
    order_db.engineer_id = engineer_id
    order_db.status = status
    order_db.updated = datetime.now()
    db.commit()
    return order_db


def order_mark_by_user(db: Session, user_id: int, order_mark: OrderMarkPost):
    # Check if the user exists
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    # Check if the order exists
    order = db.query(Order).filter(Order.id == order_mark.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order does not exist")

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


####################################################

def test_get_all_order(db: Session, user_id):
    engineer_alias = aliased(User)
    client_alias = aliased(User)
    order_db = db.query(Order, engineer_alias.name, client_alias.name, OrderIssue.name,
                        UserMarkOrder.mark) \
        .outerjoin(engineer_alias, Order.engineer_id == engineer_alias.id) \
        .outerjoin(client_alias, Order.client_id == client_alias.id) \
        .outerjoin(OrderIssue, Order.order_issue_id == OrderIssue.id) \
        .outerjoin(UserMarkOrder, and_(
        UserMarkOrder.order_id == Order.id,
        UserMarkOrder.user_id == user_id
    ))
    view_models = [test_get_order_view_model(each_order, engineer_name, client_name, issue_name, mark)
                   for each_order, engineer_name, client_name, issue_name, mark in order_db]

    return view_models
