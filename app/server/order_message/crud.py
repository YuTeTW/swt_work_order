from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.order import Order
from app.models.domain.order_issue import OrderIssue
from app.models.domain.order_message import OrderMessage
from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import User
from app.models.schemas.order import OrderModifyModel
from app.models.schemas.order_message import OrderMessageCreateModel, OrderMessageModifyModel
from app.server.authentication import AuthorityLevel
from app.server.order import OrderStatus


def create_order_message(db: Session, order_message_create, user_id: int):
    order_db = db.query(Order).filter(Order.id == order_message_create.order_id).first()
    if not order_db:
        raise HTTPException(status_code=404, detail="order doesn't exist")

    # if order_db.status == OrderStatus.close.value:
    #     raise HTTPException(status_code=400, detail="Can't create message when order close")

    try:
        db_user = OrderMessage(**order_message_create.dict(), user_id=user_id)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_order_message.__name__, description=str(e), status_code=500)
    return db_user


def get_order_message_by_order_id(db: Session, order_id: int):
    order_message_db = db.query(OrderMessage, User.name).join(User, OrderMessage.user_id == User.id).filter(
        OrderMessage.order_id == order_id).all()
    order_message_list = []
    from app.models.schemas.order_message import OrderMessageViewModel
    for order_message, reporter_name in order_message_db:
        order_message_list.append(
            OrderMessageViewModel(
                id=order_message.id,
                reporter_name=reporter_name,
                message=order_message.message,
                created_at=order_message.created_at
            )
        )
    return order_message_list


def delete_order_message_by_id(db: Session, issue_id: int):
    try:
        db.query(OrderMessage).filter(OrderMessage.id == issue_id).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=delete_order_message_by_id.__name__, description=str(e), status_code=500)
    return "Order message deleted successfully"


def modify_order_message_by_id(db: Session, order_message_modify: OrderMessageModifyModel):
    order_db = db.query(OrderMessage).filter(OrderMessage.id == order_message_modify.order_message_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_message_by_id.__name__, description='order message not found', status_code=404
        )
    try:
        order_db.user_id = order_message_modify.user_id
        order_db.message = order_message_modify.message
        order_db.updated_at = datetime.now()

        db.commit()
        db.refresh(order_db)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=modify_order_message_by_id.__name__, description=str(e), status_code=500)
    return order_db


def create_message_cause_order_info(db: Session, user_id: int, order_modify_body: OrderModifyModel):
    old_order_db = db.query(Order).filter(Order.id == order_modify_body.order_id).first()

    if not old_order_db:
        raise HTTPException(status_code=404, detail='Order not found')

    old_order_issue_db = db.query(OrderIssue).filter(OrderIssue.id == old_order_db.order_issue_id).first()
    new_order_issue_db = db.query(OrderIssue).filter(OrderIssue.id == order_modify_body.order_issue_id).first()

    if not old_order_issue_db or not new_order_issue_db:
        raise HTTPException(status_code=404, detail='Order issue not found')

    old_order_description = old_order_db.description
    new_order_description = order_modify_body.description

    old_order_detail = eval(old_order_db.detail)
    new_order_detail = order_modify_body.detail

    old_order_report_time = old_order_db.report_time
    new_order_report_time = order_modify_body.report_time

    if old_order_db.order_issue_id != order_modify_body.order_issue_id:
        create_order_message(db, OrderMessageCreateModel(
            order_id=order_modify_body.order_id,
            message=f"[Auto] ??????????????? ??? {old_order_issue_db.name} ??? ?????? ??? {new_order_issue_db.name} ??? "), user_id)

    if old_order_description != new_order_description:
        create_order_message(db, OrderMessageCreateModel(
            order_id=order_modify_body.order_id,
            message=f"[Auto] ??????????????? ??? {old_order_description} ??? ?????? ??? {new_order_description} ???"), user_id)

    if old_order_detail != new_order_detail:
        # set two list
        old_detail_set = set(old_order_detail)
        new_detail_set = set(new_order_detail)

        # find decreased detail
        decreased_list = list(old_detail_set - new_detail_set)

        # find increased detail
        increased_list = list(new_detail_set - old_detail_set)

        # create decreased order detail message
        for decreased in decreased_list:
            create_order_message(db, OrderMessageCreateModel(
                order_id=order_modify_body.order_id,
                message=f"[Auto] ????????????????????? ??? {decreased} ??? "), user_id)

        # create increased order detail message
        for increased in increased_list:
            create_order_message(db, OrderMessageCreateModel(
                order_id=order_modify_body.order_id,
                message=f"[Auto] ????????????????????? ??? {increased} ??? "), user_id)

    if old_order_report_time != new_order_report_time:
        create_order_message(db, OrderMessageCreateModel(
            order_id=order_modify_body.order_id,
            message=f"[Auto] ??????????????? ??? {old_order_report_time} ??? ?????? ??? {new_order_report_time} ???"), user_id)


def create_message_cause_status(db: Session, order_id: int, user_id: int, now_status: int, status: int):
    # change status from integer to mandarin
    name_status = {
        OrderStatus.not_appoint.value: "?????????",
        OrderStatus.working.value: "?????????",
        OrderStatus.finsh.value: "?????????",
        OrderStatus.close.value: "??????"
    }
    named_status = name_status[status]
    named_now_status = name_status[now_status]

    # auto create message
    create_order_message(db, OrderMessageCreateModel(
        order_id=order_id, message=f"[Auto] ??????????????? ??? {named_now_status} ??? ?????? ??? {named_status} ??? "), user_id)


def create_message_cause_status_and_solution(
        db: Session, order_id: int, user_id: int, now_status: int, status: int, solution: str
):
    # change status from integer to mandarin
    name_status = {
        OrderStatus.not_appoint.value: "?????????",
        OrderStatus.working.value: "?????????",
        OrderStatus.finsh.value: "?????????",
        OrderStatus.close.value: "??????"
    }
    named_status = name_status[status]
    named_now_status = name_status[now_status]

    # auto create message
    create_order_message(db, OrderMessageCreateModel(
        order_id=order_id, message=f"[Auto] ??????????????? ??? {named_now_status} ??? ?????? ??? {named_status} ??? "), user_id)

    create_order_message(db, OrderMessageCreateModel(
        order_id=order_id, message=f"[Auto] ?????????????????????????????? ??? {solution} ??? "), user_id)


def create_message_cause_engineer(db: Session, order_id: int, now_engineer_id: int, engineer_id: int, user_id):
    # change engineer name from id to mandarin
    now_engineer_db = db.query(User).filter(User.id == now_engineer_id).first()
    after_engineer_db = db.query(User).filter(User.id == engineer_id).first()

    # check order is appointed or not
    if now_engineer_db and now_engineer_db.level == AuthorityLevel.engineer.value:
        now_engineer_name = now_engineer_db.name
    else:
        now_engineer_name = "?????????"

    after_engineer_name = after_engineer_db.name

    # auto create message
    create_order_message(db,
                         OrderMessageCreateModel(
                             order_id=order_id,
                             message=f"[Auto] ???????????????????????? ??? {now_engineer_name} ??? ?????? ??? {after_engineer_name} ???"
                         ),
                         user_id)


def create_message_cause_file(db: Session, order_id: int, user_id: int, filename: str, act):
    # auto create message
    if act == "upload":
        message = f"[Auto] ??????????????? ??? {filename} ???"
    else:
        message = f"[Auto] ??????????????? ??? {filename} ???"
    create_order_message(db,
                         OrderMessageCreateModel(
                             order_id=order_id,
                             message=message
                         ),
                         user_id)
