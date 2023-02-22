from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey

from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), index=True)
    engineer_id = Column(Integer, ForeignKey("users.id"), index=True, default=0)
    order_issue_id = Column(Integer, ForeignKey("order_issue.id"), index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), index=True)
    serial_number = Column(String, default="")
    company_name = Column(String)
    status = Column(Integer, index=True, default=0)
    mark = Column(Boolean, default=False)
    description = Column(String, default=None)
    detail = Column(String, default=None)  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    file_name = Column(String, default=str([]))  # 因sqlite不能用Array存，所以先轉str，再轉list輸出
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime)


    def __init__(self, client_id, company_name, reporter_id,
                 order_issue_id, description, detail, **kwargs):
        self.client_id = client_id
        self.order_issue_id = order_issue_id
        self.reporter_id = reporter_id
        self.company_name = company_name
        self.description = description
        self.detail = detail
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return 'id={},client_id={}, engineer_id={}, order_issue_id={},serial_number={},company_name={},status={},' \
               ' mark={}, detail={}, description={}, file_name={}'.format(
                self.id, self.client_id, self.engineer_id, self.order_issue_id, self.serial_number, self.company_name,
                self.status, self.mark, self.detail, self.description, self.created_at, self.updated_at
                )
