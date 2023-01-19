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
    is_enable = Column(Boolean, index=True, default=False)


    def __init__(self, email, password, name, info, is_enable, level, group_id, **kwargs):
        self.email = email
        self.password = password
        self.name = name
        self.is_enable = is_enable
        self.info = info
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.level = level
        self.group_id = group_id
        self.verify_code_enable = False

    def __repr__(self):
        return 'id={},group_id={}, email={}, name={},info={}'.format(
            self.id, self.group_id, self.email, self.name, self.info, self.created_at, self.updated_at
        )
