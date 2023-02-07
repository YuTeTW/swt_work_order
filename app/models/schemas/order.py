from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class OrderBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class OrderCreateModel(OrderBase):
    order_issue_id: int
    serial_number: str
    description: str
    detail: list

    class Config:
        schema_extra = {
            "example": {
                "order_issue_id": 1,
                "serial_number": "A-1",
                "description": "開機很久",
                "detail": [
                    "問題1",
                    "問題2",
                    "問題3"
                ]
            }
        }


class OrderCreateResponseModel(OrderBase):
    order_issue_id: int
    serial_number: str
    description: str
    detail: list


class OrderFilterBodyModel(OrderBase):
    user_id: list = []
    order_issue_id: list = []
    engineer_id: list = []
    status: list = []


class OrderViewinfoModel(OrderBase):
    status_name: str
    engineer_name: str
    order_issue_name: str


class OrderViewModel(OrderBase):
    company_name: str
    serial_number: str
    description: str
    detail: list
    mark: bool
    status: int
    created_at: datetime
    engineer_name: str
    issue_name: str


class OrderView2Model(OrderBase):
    a: int
    b: int
    all_order: OrderViewModel


class OrderDeleteIdModel(OrderBase):
    order_id_list: list


class OrderModifyModel(OrderBase):
    order_id: int
    order_issue_id: int
    serial_number: str
    description: str
    detail: str
