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


def get_order_engineer_id(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    return order_db.engineer_id


def get_order_status(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    return order_db.status


def get_order_reporter(db: Session, order_id: int):
    order_db = db.query(Order).filter(Order.id == order_id).first()
    return order_db.reporter_id


def create_order(db: Session, reporter_id: int, company_name, order_create: OrderCreateModel):
    if not db.query(User).filter(User.id == order_create.client_id).first():
        raise HTTPException(status_code=404, detail='client user not found')

    if not db.query(OrderIssue).filter(OrderIssue.id == order_create.order_issue_id).first():
        raise HTTPException(status_code=404, detail='order issue not found')

    if not db.query(User).filter(User.id == reporter_id).first():
        raise HTTPException(status_code=404, detail='order issue not found')

    default_engineer = db.query(User).filter(User.level == -1).first()
    if not default_engineer:
        raise HTTPException(status_code=404, detail='order issue not found')

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


def get_order_view_model(each_order, engineer_name, issue_name, mark):
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
        company_name="SOMETHING WRONG",
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

    # engineer can get principal order and not appoint order
    if level == AuthorityLevel.engineer.value:
        default_engineer = db.query(User).filter_by(level=-1).first()
        order_db = order_db.filter(Order.engineer_id.in_([default_engineer.id, user_id]))

    # client only get self orders
    if level == AuthorityLevel.client.value:
        order_db = order_db.filter(Order.client_id == user_id)

    # filter start time
    if start_time:
        order_db = order_db.filter(Order.created_at > start_time)

    # filter end time
    if end_time:
        order_db = order_db.filter(Order.created_at < end_time)

    # return order_db.all()

    view_models = [get_order_view_model(each_order, engineer_name, issue_name, mark)
                   for each_order, engineer_name, issue_name, mark in order_db]
    return view_models


def get_some_order(db: Session, user_id, client_id_list, engineer_id_list, order_issue_id_list, status_list,
                   start_time, end_time):
    # Join the Order table with the User and OrderIssue tables
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

    if client_id_list:
        order_db = order_db.filter(Order.client_id.in_(client_id_list))
    if engineer_id_list:
        order_db = order_db.filter(Order.engineer_id.in_(engineer_id_list))
    if order_issue_id_list:
        order_db = order_db.filter(Order.order_issue_id.in_(order_issue_id_list))
    if status_list:
        order_db = order_db.filter(Order.status.in_(status_list))
    if start_time:
        order_db = order_db.filter(Order.created_at > start_time)
    if end_time:
        order_db = order_db.filter(Order.created_at < end_time)

    # Convert each order to a view model
    view_models = [get_order_view_model(each_order, engineer_name, issue_name, mark)
                   for each_order, engineer_name, issue_name, mark in order_db]

    return view_models


def get_a_order(db, order_id, user_id):
    # Join the Order table with the User and OrderIssue tables
    order_db = db.query(Order, User.name, OrderIssue.name, UserMarkOrder.mark).outerjoin(
        User, Order.engineer_id == User.id
    ).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id
    ).outerjoin(
        UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == user_id
        )
    ).filter(Order.id == order_id)

    view_models = [get_order_view_model(each_order, engineer_name, issue_name, mark)
                   for each_order, engineer_name, issue_name, mark in order_db]

    return view_models[0]


def check_order_status(db: Session, order_id_list):
    order_db = db.query(Order).filter(Order.id.in_(order_id_list), Order.status != 0).first()
    if order_db:
        status = order_db.status
    else:
        status = None
    return status


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
        if now_status != 2:
            raise HTTPException(
                status_code=401,
                detail="client only can change status when order finish"
            )
        if status not in [1, 3] and status != 2:
            raise HTTPException(
                status_code=401,
                detail="client only can change status to 'in process' or 'closing order' when order finish"
            )

    # check engineer change status auth
    elif level == AuthorityLevel.engineer.value:  # engineer
        if status in [3, 0]:
            raise HTTPException(
                status_code=401,
                detail="engineer only can change status to not appoint or finish"
            )
        if status == 1 and not db.query(Order).filter(Order.engineer_id == current_user_id).first():
            raise HTTPException(
                status_code=401,
                detail="engineer only can change principle order status"
            )
    # check pm change status auth
    elif level == AuthorityLevel.pm.value:  # pm
        order_db = db.query(Order).filter(Order.id == order_id).first()
        if status == 3 and order_db.created_at + timedelta(days=7) > datetime.now():
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

    if not order_db:
        raise HTTPException(status_code=404, detail="order not found")

    status = 1 if order_db.status == 0 else order_db.status
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
                        UserMarkOrder.mark).select_from(Order)
    order_db.outerjoin(
        engineer_alias, Order.engineer_id == engineer_alias.id
    ).outerjoin(
        client_alias, Order.client_id == client_alias.id
    ).outerjoin(
        OrderIssue, Order.order_issue_id == OrderIssue.id
    ).outerjoin(
        UserMarkOrder, and_(
            UserMarkOrder.order_id == Order.id,
            UserMarkOrder.user_id == user_id
        )
    )

    # print(order_db)
    #
    # order_db = db.query(Order, User.name, OrderIssue.name, UserMarkOrder.mark).outerjoin(
    #     User, Order.engineer_id == User.id
    # ).outerjoin(
    #     OrderIssue, Order.order_issue_id == OrderIssue.id
    # ).outerjoin(
    #     UserMarkOrder, and_(
    #         UserMarkOrder.order_id == Order.id,
    #         UserMarkOrder.user_id == user_id
    #     )
    # )

    order = order_db.all()

    print(order)
    # # engineer can get principal order and not appoint order
    # if level == AuthorityLevel.engineer.value:
    #     default_engineer = db.query(User).filter_by(level=-1).first()
    #     order_db = order_db.filter(Order.engineer_id.in_([default_engineer.id, user_id]))
    #
    # # client only get self orders
    # if level == AuthorityLevel.client.value:
    #     order_db = order_db.filter(Order.client_id == user_id)
    #
    # # filter start time
    # if start_time:
    #     order_db = order_db.filter(Order.created_at > start_time)
    #
    # # filter end time
    # if end_time:
    #     order_db = order_db.filter(Order.created_at < end_time)
    #
    # # return order_db.all()
    #
    # view_models = [get_order_view_model(each_order, engineer_name, client_name, issue_name, mark)
    #                for each_order, engineer_name, client_name, issue_name, mark in order_db]
    # return view_models

