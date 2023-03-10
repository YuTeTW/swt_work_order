from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class OrderBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class OrderCreateModel(OrderBase):
    client_id: int
    order_issue_id: int
    description: str
    detail: List[str]
    report_time: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "client_id": 1,
                "order_issue_id": 1,
                "description": "開機很久",
                "detail": [
                    "問題1",
                    "問題2",
                    "問題3"
                ]
            }
        }


class OrderCreateResponseModel(OrderBase):
    id: int
    order_issue_id: int
    description: str
    detail: list
    report_time: datetime


class OrderFilterBodyModel(OrderBase):
    client_id_list: list = []
    order_issue_id_list: list = []
    engineer_id_list: list = []
    status_list: list = []


class OrderViewinfoModel(OrderBase):
    status_name: str
    engineer_name: str
    order_issue_name: str


class OrderViewModel(OrderBase):
    id: int
    reporter_id: int
    company_name: str
    mark: bool
    status: int
    engineer_name: str
    issue_name: str
    file_name: list
    description: str
    detail: list
    report_time: datetime
    created_at: datetime
    updated_at: datetime



class OrderViewModel2(OrderBase):
    Order: OrderViewModel
    engineer_name: str
    issue_name: str
# def __init__(self, order, engineer_name, issue_name, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.id = order.id
    #     self.company_name = order.company_name
    #     self.serial_number = order.serial_number
    #     self.description = order.description
    #     self.detail = eval(order.detail)
    #     self.engineer_name = engineer_name if engineer_name else "未指派"
    #     self.issue_name = issue_name if issue_name else "未選擇問題種類"
    #     self.mark = order.mark
    #     self.status = order.status
    #     self.created_at = order.created_at
    #     self.file_name = eval(order.file_name)


class OrderView2Model(OrderBase):
    a: int
    b: int
    all_order: OrderViewModel


class OrderDeleteIdModel(OrderBase):
    order_id_list: list


class OrderModifyModel(OrderBase):
    order_id: int
    order_issue_id: int
    description: str
    detail: list
    report_time: str


class OrderMarkPost(OrderBase):
    order_id: int
    mark: bool


class OrderGetFilterTimeModel(OrderBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
