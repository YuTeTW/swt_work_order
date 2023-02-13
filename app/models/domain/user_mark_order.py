from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


class UserMarkOrder(Base):
    __tablename__ = "user_mark_order"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    mark = Column(Boolean, default=False)
    created_at = Column(DateTime, index=True, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    # user = relationship("User", back_populates="marked_orders")
    # order = relationship("Order", back_populates="marked_by_users")


    def __init__(self, user_id, order_id, mark, **kwargs):
        self.user_id = user_id
        self.order_id = order_id
        self.mark = mark


    def __repr__(self):
        return 'id={}, user_id={}, order_id={},mark={}'.format(
            self.id, self.user_id, self.order_id, self.mark)
