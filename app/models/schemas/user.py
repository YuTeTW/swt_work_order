from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UserInfoModel(UserBase):
    telephone_number: str = ""
    line_id: str
    note: str = ""
    office_hours: str = ""


class UserPostViewModel(UserBase):
    email: EmailStr
    password: str
    name: str
    info: UserInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "root",
                "password": "root",
                "email": "root@fastwise.net",
                "info": {
                    "telephone_number": "0987654321",
                    "line_id": "@kadiggec",
                    "note": "nothing",
                    "office_hours": "8AM-6PM"
                }
            }
        }


class UserPatchInfoModel(UserBase):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "swt",
            }
        }


class UserChangeSettingModel(UserBase):
    email_alert: Optional[bool] = -1
    device_email_alert: Optional[bool] = -1
    language: Optional[int] = -1

    class Config:
        schema_extra = {
            "example": {
                "email_alert": False,
                "device_email_alert": False,
                "language": 0,
            }
        }


# class UserPatchAccountViewModel(UserBase):
#     email: EmailStr
#
#     class Config:
#         schema_extra = {
#             "example": {
#                 "email": "ricky400430012@fastwise.net",
#             }
#         }


class UserPatchPasswordViewModel(UserBase):
    new_password: str
    old_password: str

    class Config:
        schema_extra = {
            "example": {
                "new_password": "ricky4004",
                "old_password": "ricky4004"
            }
        }


class UserLoginViewModel(UserBase):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "swt@fastwise.net",
                "password": "swt"
            }
        }


class UserViewModel(UserBase):
    id: int
    email: str
    name: str
    info: UserInfoModel
    level: int
    created_at: datetime
    updated_at: datetime


class LoginResultUserViewModel(UserBase):
    User: UserViewModel
    Status: bool
    access_token: str
    refresh_token: str
    token_type: str


class DeviceLoginResultUserViewModel(UserBase):
    User: UserViewModel
    access_token: str
    refresh_token: str
    token_type: str


class UserInviteViewModel(UserBase):
    email: EmailStr
    level: int
