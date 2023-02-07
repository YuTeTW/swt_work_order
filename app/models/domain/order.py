from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    engineer_id = Column(Integer, ForeignKey("users.id"), default=0)
    order_issue_id = Column(Integer, ForeignKey("order_issue.id"))
    serial_number = Column(String, index=True)
    company_name = Column(String, index=True)
    status = Column(Integer, index=True, default=0)
    mark = Column(Boolean, index=True, default=False)
    description = Column(String, index=True, default=None)
    detail = Column(String, index=True, default=None)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    file_name = Column(String, index=True, default=None)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, client_id, engineer_id, serial_number, company_name,
                 status, order_issue_id, description, detail, file_name, **kwargs):
        self.client_id = client_id
        self.engineer_id = engineer_id
        self.order_issue_id = order_issue_id
        self.serial_number = serial_number
        self.company_name = company_name
        self.status = status
        self.description = description
        self.detail = detail
        self.file_name = file_name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    # def __repr__(self):
    #     return 'id={},group_id={}, email={}, name={},info={}'.format(
    #         self.id, self.group_id, self.email, self.name, self.info, self.created_at, self.updated_at
    #     )
