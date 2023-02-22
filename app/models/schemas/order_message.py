from datetime import datetime
from pydantic import BaseModel


class OrderBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class OrderMessageCreateModel(OrderBase):
    order_id: int
    message: str


    class Config:
        schema_extra = {
            "example": {
                "order_id": 1,
                "message": "修改第一次",
            }
        }


class OrderMessageCreateInModifyModel():
    pass
    # order_id =
    # message
    #
    # def __int__(self, order_id, message):
    #     self.order_id = order_id
    #     self.message = message


class OrderMessageCreateViewModel(OrderBase):
    id: int
    reporter_name: str
    message: str
    created_at: datetime


class OrderMessageViewModel(OrderBase):
    id: int
    reporter_name: str
    message: str
    created_at: datetime


class OrderMessageModifyModel(OrderBase):
    order_message_id: int
    user_id: int
    message: str
