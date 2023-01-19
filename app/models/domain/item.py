from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class OrderMessage(Base):
    __tablename__ = "order_message"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    message = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, order_id, user_id, message, **kwargs):
        self.order_id = order_id
        self.user_id = user_id
        self.message = message
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


    def __repr__(self):
        return 'id={},group_id={}, email={}, name={},info={}'.format(
            self.id, self.group_id, self.email, self.name, self.info, self.created_at, self.updated_at
        )
