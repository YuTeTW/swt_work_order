from pydantic import BaseModel


class OrderBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class OrderIssueCreateModel(OrderBase):
    name: str
    severity: int
    time_hours: float

    class Config:
        schema_extra = {
            "example": {
                "name": "電腦故障",
                "severity": 3,
                "time_hours": 3
            }
        }


class OrderIssueViewModel(OrderBase):
    id: int
    name: str
    severity: int
    time_hours: float


class OrderIssueModifyModel(OrderBase):
    order_issue_id: int
    name: str
    severity: int
    time_hours: float
