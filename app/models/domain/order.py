from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.domain.order_issue import OrderIssue
from app.models.domain.user import User


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), index=True)
    engineer_id = Column(Integer, ForeignKey("users.id"), index=True)
    order_issue_id = Column(Integer, ForeignKey("order_issue.id"), index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), index=True)
    serial_number = Column(String, default="")
    solution = Column(String, default="")
    status = Column(Integer, index=True, default=0)
    description = Column(String, default=None)
    detail = Column(String, default=None)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    file_name = Column(String, default=str([]))  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    report_time = Column(DateTime, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime)

    def __init__(self, client_id, reporter_id, engineer_id, serial_number,
                 order_issue_id, description, detail, report_time, **kwargs):
        self.client_id = client_id
        self.order_issue_id = order_issue_id
        self.reporter_id = reporter_id
        self.engineer_id = engineer_id
        self.description = description
        self.detail = detail
        self.serial_number = serial_number
        self.report_time = report_time or datetime.now()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        # if report_time:
        #     self.report_time = report_time
        # else:
        #     datetime.now()

    def __repr__(self):
        return 'id={},client_id={}, engineer_id={}, order_issue_id={},serial_number={},status={},' \
               'detail={}, description={}, file_name={}'.format(
                self.id, self.client_id, self.engineer_id, self.order_issue_id, self.serial_number,
                self.status, self.detail, self.description, self.created_at, self.updated_at
                )
