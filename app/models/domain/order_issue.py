from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, FLOAT

from app.db.database import Base


class OrderIssue(Base):
    __tablename__ = "order_issue"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    severity = Column(Integer)
    time_hours = Column(FLOAT)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, name, severity, time_hours, **kwargs):
        self.name = name
        self.severity = severity
        self.time_hours = time_hours
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


    def __repr__(self):
        return 'id={},name={}, severity={}, time_hours={}'.format(
            self.id, self.name, self.severity, self.time_hours, self.created_at, self.updated_at
        )
