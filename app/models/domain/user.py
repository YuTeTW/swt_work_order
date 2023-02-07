from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    level = Column(Integer, index=True, default=-1)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    is_enable = Column(Boolean, index=True, default=True)
    info = Column(JSON)


    def __init__(self, email, password, name, info, is_enable, level, **kwargs):
        self.email = email
        self.password = password
        self.name = name
        self.is_enable = is_enable
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.level = level

    def __repr__(self):
        return 'id={}, email={}, name={},info={},is_enable={}'.format(
            self.id, self.email, self.name, self.info, self.is_enable, self.created_at, self.updated_at
        )
