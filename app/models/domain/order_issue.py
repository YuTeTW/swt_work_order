from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime

from app.db.database import Base


class OrderIssue(Base):
    __tablename__ = "order_issue"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    severity = Column(Integer)
    time_hours = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(self, name, severity, time_hours, **kwargs):
        self.name = name
        self.severity = severity
        self.time_hours = time_hours


    def __repr__(self):
        return 'id={},name={}, severity={}, time_hours={}'.format(
            self.id, self.name, self.severity, self.time_hours, self.created_at, self.updated_at
        )
