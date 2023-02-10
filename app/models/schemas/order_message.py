from datetime import datetime
from pydantic import BaseModel


class OrderBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class OrderMessageCreateModel(OrderBase):
    user_id: int
    order_id: int
    message: str

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "order_id": 1,
                "message": "修改第一次",
            }
        }


class OrderMessageViewModel(OrderBase):
    id: int
    reporter_name: str
    message: str
    created_at: datetime


class OrderMessageModifyModel(OrderBase):
    order_message_id: int
    report_name: str
    detail: str
