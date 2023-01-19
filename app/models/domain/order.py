from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("user.id"))
    engineer_id = Column(Integer, ForeignKey("user.id"))
    serial_number = Column(String, index=True)
    name = Column(String, index=True)
    status = Column(Integer, index=True, default=0)
    type = Column(Integer, index=True)
    description = Column(String, index=True, default=False)
    note = Column(String, index=True, default=None)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)

    def __init__(self, client_id, engineer_id, serial_number, name, status, type, description, note, **kwargs):
        self.client_id = client_id
        self.engineer_id = engineer_id
        self.serial_number = serial_number
        self.name = name
        self.status = status
        self.type = type
        self.description = description
        self.note = note
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return 'id={},group_id={}, email={}, name={},info={}'.format(
            self.id, self.group_id, self.email, self.name, self.info, self.created_at, self.updated_at
        )
