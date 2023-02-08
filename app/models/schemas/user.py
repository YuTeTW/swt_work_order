from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UserInfoModel(UserBase):
    telephone_number: str = ""
    line: str
    note: str = ""
    office_hours: str = ""


class UserCreateModel(UserBase):
    level: int
    email: EmailStr
    password: str
    name: str
    info: UserInfoModel

    class Config:
        schema_extra = {
            "example": {
                "level": 2,
                "name": "root",
                "email": "root@fastwise.net",
                "password": "root",
                "info": {
                    "contact_email": "root@fastwise.net",
                    "telephone_number": "0987654321",
                    "line": "@kadiggec",
                    "note": "nothing",
                }
            }
        }


class UserPatchInfoModel(UserBase):
    user_id: int
    level: int
    name: str
    contact_email: str
    telephone_number: str = ""
    line: str
    note: str = ""

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "level": 3,
                "name": "root",
                "contact_email": "test@fastwise.net",
                "telephone_number": "0987654321",
                "line": "@kadiggec",
                "note": "nothing"
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
