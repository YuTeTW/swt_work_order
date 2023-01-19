from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UserInfoModel(UserBase):
    address: str = ""
    country: str = ""
    telephone_number: str = ""
    companyScale: str = ""
    usage: str = ""
    industry: str = ""
    email_alert: bool = False
    device_email_alert: bool = False
    language: int = 0


class AdminUserPostViewModel(UserBase):
    email: EmailStr
    password: str
    name: str
    info: UserInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky400430012",
                "password": "ricky400430012",
                "email": "ricky400430012@gmail.com",
                "info": {
                    "address": "台北市中山區民權東路一段",
                    "telephone_number": "0987654321",
                    "usage": "商用",
                    "country": "Taiwan",
                    "company_scale": "10~50",
                    "industry": "軟體業",
                    "area": "False",
                    "language": "0"
                },
                "group": {
                    "name": "ricky_group"
                }
            }
        }


class UserPostViewModel(UserBase):
    email: EmailStr
    password: str
    name: str
    info: UserInfoModel

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky400430012",
                "password": "ricky400430012",
                "email": "ricky400430012@gmail.com",
                "info": {
                    "address": "台北市中山區民權東路一段",
                    "telephone_number": "0987654321",
                    "usage": "商用",
                    "country": "Taiwan",
                    "company_scale": "10~50",
                    "industry": "軟體業",
                    "area": "False",
                    "language": "0"
                }
            }
        }


class UserPatchInfoModel(UserBase):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "ricky4004",
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
                "email": "ricky4004@gmail.com",
                "password": "ricky4004"
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
