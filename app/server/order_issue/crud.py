from typing import Union

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain.order_issue import OrderIssue
from app.models.domain.Error_handler import UnicornException
from app.models.schemas.order_issue import OrderIssueViewModel, OrderIssueCreateModel


def create_order_issue(db: Session, order_issue_create: OrderIssueCreateModel) -> OrderIssueViewModel:

    # Check issue name exist or not
    if db.query(OrderIssue).filter(OrderIssue.name == order_issue_create.name).first():
        raise HTTPException(status_code=400, detail="Issue name already exist")

    # Check severity range
    if not isinstance(order_issue_create.severity, int) or order_issue_create.severity < 0:
        raise HTTPException(status_code=400, detail="Issue severity must be a positive integer")

    # Check time range
    if isinstance(order_issue_create.time_hours, float) or order_issue_create.time_hours < 0:
        raise HTTPException(status_code=400, detail="Issue time hours have to more than 0")

    try:

        # Create order issue
        db_user = OrderIssue(**order_issue_create.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(str(e))
        raise UnicornException(name=create_order_issue.__name__, description=str(e), status_code=500)
    return db_user


def get_all_order_issue(db: Session) -> list:
    return db.query(OrderIssue).all()


def delete_order_issue_by_id(db: Session, issue_id: int) -> str:
    try:

        # Change order to none order issue
        from app.models.domain.order import Order
        order_db = db.query(Order).filter(Order.order_issue_id == issue_id).all()
        if order_db:
            for each_order in order_db:
                each_order.order_issue_id = 0

        # Delete order issue
        db.query(OrderIssue).filter(OrderIssue.id == issue_id).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=delete_order_issue_by_id.__name__, description=str(e), status_code=500)
    return "Order issue deleted successfully"


def modify_order_issue_by_id(db: Session, order_issue_modify) -> OrderIssueViewModel:
    order_db = db.query(OrderIssue).filter(OrderIssue.id == order_issue_modify.order_issue_id).first()

    # Check order issue exist
    if not order_db:
        raise UnicornException(
            name=modify_order_issue_by_id.__name__, description='order issue not found', status_code=404
        )

    # Check issue name exist or not
    if db.query(OrderIssue.name).filter(and_(
            OrderIssue.id != order_issue_modify.order_issue_id,
            OrderIssue.name == order_issue_modify.name)).first():
        raise UnicornException(
            name=modify_order_issue_by_id.__name__, description='order issue name already exist', status_code=400
        )
    
    # Check severity range
    if not isinstance(order_issue_modify.severity, int) or order_issue_modify.severity < 0:
        raise HTTPException(status_code=400, detail="Issue severity must be a positive integer")
    
    # Check time range
    if not isinstance(order_issue_modify.time_hours, float) or order_issue_modify.time_hours < 0:
        raise HTTPException(status_code=400, detail="Issue time hours have to more than 0")
    
    try:
        # Modify order issue
        order_db.name = order_issue_modify.name
        order_db.severity = order_issue_modify.severity
        order_db.time_hours = order_issue_modify.time_hours
        order_db.updated_at = datetime.now()
        db.commit()
    except Exception as e:
        db.rollback()
        raise UnicornException(name=modify_order_issue_by_id.__name__, description=str(e), status_code=500)
    return order_db
