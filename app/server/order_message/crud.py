from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.order import Order
from app.models.domain.order_message import OrderMessage
from app.models.domain.Error_handler import UnicornException
from app.models.domain.user import User


def create_order_message(db: Session, order_message_create, user_id):
    if not db.query(Order).filter(Order.id == order_message_create.order_id).first():
        raise UnicornException(
            name=modify_order_message_by_id.__name__, description="order doesn't exist", status_code=404
        )
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


def modify_order_message_by_id(db: Session, order_message_modify):
    order_db = db.query(OrderMessage).filter(OrderMessage.id == order_message_modify.order_message_id).first()
    if not order_db:
        raise UnicornException(
            name=modify_order_message_by_id.__name__, description='order message not found', status_code=404
        )
    order_db.update(
        {
            "name": order_message_modify.name,
            "severity": order_message_modify.severity,
            "time_hours": order_message_modify.time_hours,
            "updated_at": datetime.now()
        }
    )
    db.commit()
    return order_db
