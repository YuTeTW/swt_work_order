from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    level = Column(Integer, index=True, default=-1)
    is_enable = Column(Boolean, default=True)
    status = Column(Integer, index=True)
    info = Column(JSON)
    created_at = Column(DateTime, index=True, default=datetime.now())
    updated_at = Column(DateTime, index=True, default=datetime.now())


    def __init__(self, email, password, name, info, is_enable, level, status, **kwargs):
        self.email = email
        self.password = password
        self.name = name
        self.is_enable = is_enable
        self.level = level
        self.status = status
        self.info = info


    def __repr__(self):
        return 'id={}, email={}, name={},info={},is_enable={}'.format(
            self.id, self.email, self.name, self.info, self.is_enable, self.created_at, self.updated_at
        )
