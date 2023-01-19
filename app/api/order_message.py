# from fastapi import APIRouter, Depends, HTTPException
# from typing import List
# from starlette.templating import Jinja2Templates
# from starlette.requests import Request
# from fastapi_jwt_auth import AuthJWT
# from sqlalchemy.orm import Session
# from starlette.background import BackgroundTasks
#
# from app.db.database import get_db
# from app.helper.authentication import authorize_user
# from app.server.authentication import AuthorityLevel, verify_password, check_level, get_email_token
#
# from app.server.send_email import send_invite_mail
# import datetime
# from app.server.user.crud import (
#     create_user,
#     get_user_by_email,
#     get_user_by_name,
#     get_all_users,
#     check_email_exist,
#     modify_user,
#     get_user_by_name_in_group,
#     modify_user_password,
#     change_user_setting,
#     change_user_verify_code_enable,
#     get_users_in_group,
#     get_user_by_id,
#     delete_group_by_group_id,
#     check_user_owner,
#     delete_user_by_user_id,
#     check_RD_user_exist
# )
# from app.models.schemas.user import (
#     UserViewModel,
#     UserPostViewModel,
#     AdminUserPostViewModel,
#     UserPatchInfoModel,
#     UserPatchPasswordViewModel,
#     UserChangeSettingModel,
#     UserInviteViewModel
# )
#
# router = APIRouter()
# templates = Jinja2Templates(directory="templates")
#
#
# # 取得所有User (RD)
# @router.get("/users/GetAllUsers", response_model=List[UserViewModel])
#
