from fastapi import APIRouter, Depends, HTTPException
from typing import List
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel, verify_password, check_level, get_email_token

from app.server.send_email import send_invite_mail
import datetime
from app.server.user.crud import (
    create_user,
    get_user_by_email,
    get_user_by_name,
    get_all_users,
    check_email_exist,
    modify_user,
    get_user_by_name_in_group,
    modify_user_password,
    change_user_setting,
    change_user_verify_code_enable,
    get_users_in_group,
    get_user_by_id,
    delete_group_by_group_id,
    check_user_owner,
    delete_user_by_user_id,
    check_root_exist, check_user_exist
)
from app.models.schemas.user import (
    UserViewModel,
    UserPostViewModel,
    AdminUserPostViewModel,
    UserPatchInfoModel,
    UserPatchPasswordViewModel,
    UserChangeSettingModel,
    UserInviteViewModel
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# 取得所有User (RD)
@router.get("/user", response_model=List[UserViewModel])
def RD_get_all_users(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if not check_level(current_user, AuthorityLevel.root.value):
        raise HTTPException(status_code=401, detail="權限不夠")

    return get_all_users(db)


# user id 修改 User Info(HRAccess)
@router.patch("/user/info", response_model=UserViewModel)
def patch_user_info(userPatch: UserPatchInfoModel,
                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    user_db = get_user_by_name_in_group(db, userPatch.name, current_user.group_id)
    if user_db:
        if user_db.id != current_user.id:
            raise HTTPException(status_code=400, detail="Name already exist in this group")

    return modify_user(db, current_user, userPatch)


# user id 修改 密碼 (HRAccess)
@router.patch("/user/password", response_model=UserViewModel)
def patch_user_password(userPatch: UserPatchPasswordViewModel, db: Session = Depends(get_db),
                        Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if not verify_password(userPatch.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="舊密碼錯誤")

    return modify_user_password(db, current_user.id, userPatch)


# user id 修改 User setting (HRAccess)
@router.patch("/user/setting", response_model=UserViewModel)
def patch_user_setting(userPatch: UserChangeSettingModel,
                       db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    return change_user_setting(db, current_user.id, userPatch)


# user id 修改 User is_enable (HRAccess)
@router.patch("/user/verify_code_enable", response_model=UserViewModel)
def patch_user_verify_code_enable(verify_code_enable: bool, db: Session = Depends(get_db),
                                  Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    return change_user_verify_code_enable(db, current_user.id, verify_code_enable)


# 刪除 user (Admin)
@router.delete("/user", response_model=UserViewModel)
def delete_a_user(user_id: int,
                  db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if not check_level(current_user, AuthorityLevel.admin.value):
        raise HTTPException(status_code=401, detail="Unauthorized")

    be_deleted_user = check_user_exist(db, user_id)
    if not be_deleted_user:
        raise HTTPException(status_code=400, detail="User doesn't exist")

    if be_deleted_user.level <= current_user.level:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return delete_user_by_user_id(db, be_deleted_user.id)


# 創建 User
@router.post("/user/create", response_model=UserViewModel)
def create_a_user(user_create: UserPostViewModel, level: int,
                  Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)
    if current_user.level >= level or current_user.level >= 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if get_user_by_email(db, email=user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_db = create_user(db, user_create, level)
    return user_db


#######################################################################################################################
# 創建 root
@router.post("/user/root", response_model=UserViewModel)
def create_root(user_data: UserPostViewModel, db: Session = Depends(get_db)):
    if check_root_exist(db):
        raise HTTPException(status_code=400, detail="root already exist")
    user_db = create_user(db, user_data, level=AuthorityLevel.root.value)

    return user_db
