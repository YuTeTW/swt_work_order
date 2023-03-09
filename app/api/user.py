from fastapi import APIRouter, Depends, HTTPException
from typing import List
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel, verify_password, check_level
from app.server.authentication.crud import set_user_enable
from app.server.user import UserStatus
from app.server.user.crud import (
    create_user,
    get_user_by_email,
    get_all_users,
    modify_user,
    modify_user_password,
    delete_user_by_user_id,
    check_root_exist,
    check_user_exist,
    get_user_by_id,
    get_user_by_level
)
from app.models.schemas.user import (
    UserViewModel,
    UserCreateModel,
    UserPatchInfoModel,
    UserPatchPasswordModel,
)

router = APIRouter()


# 創建 User
@router.post("/user/create", response_model=UserViewModel)
def create_a_user(user_create: UserCreateModel,
                  Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)

    # user level doesn't exist
    if user_create.level > AuthorityLevel.client.value or user_create.level < AuthorityLevel.root.value:
        raise HTTPException(status_code=405, detail="Method Not Allowed")

    # check create user authorize
    if current_user.level > user_create.level or current_user.level >= 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # check account
    if get_user_by_email(db, email=user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_db = create_user(db, user_create)
    return user_db


# 取得單一User
@router.get("/user", response_model=UserViewModel)
def get_a_user_by_id(user_id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if not check_level(current_user, AuthorityLevel.pm.value):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return get_user_by_id(db, user_id)


# 取得所有User
@router.get("/user/all", response_model=List[UserViewModel])
def get_all_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if not check_level(current_user, AuthorityLevel.pm.value):
        raise HTTPException(status_code=401, detail="Online pm can get all user")

    return get_all_users(db)


# 取得User by level
@router.get("/user/level/{level}", response_model=List[UserViewModel])
def get_users_by_level(level: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level == AuthorityLevel.client.value:
        raise HTTPException(status_code=401, detail="client can't get other user")

    if current_user.level > level:
        raise HTTPException(status_code=401, detail="Your level doesn't enough")

    return get_user_by_level(db, level)


# user id 修改 User Info
@router.patch("/user/info", response_model=UserViewModel)
def patch_user_info(user_patch: UserPatchInfoModel,
                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    # Can't change level to same level or higher lever
    if user_patch >= current_user.level:
        raise HTTPException(status_code=401, detail="can't change level to same level or higher lever")

    # check pm can't modify other pm
    patch_user_db = get_user_by_id(db, user_patch.user_id)
    if current_user.level == AuthorityLevel.pm.value and \
            patch_user_db.level == AuthorityLevel.pm.value and \
            current_user.id != user_patch.user_id:
        raise HTTPException(status_code=401, detail="pm can't modify other pm")

    # check client and engineer only can change its info
    if current_user.level == AuthorityLevel.engineer.value or current_user.level == AuthorityLevel.client.value:
        if current_user.id != user_patch.user_id:
            raise HTTPException(status_code=401, detail="engineer and client only can modify himself")

    # can't modify root
    if user_patch.level == AuthorityLevel.root.value:
        raise HTTPException(status_code=401, detail="Can't modify root")

    return modify_user(db, user_patch)


# user id 修改密碼
@router.patch("/user/password", response_model=UserViewModel)
def patch_user_password(userPatch: UserPatchPasswordModel, db: Session = Depends(get_db),
                        Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if not verify_password(userPatch.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    return modify_user_password(db, current_user.id, userPatch)


# user id 修改 User is_enable (HRAccess)
@router.patch("/user/is_enable", response_model=UserViewModel)
def patch_user_is_enable(user_id: int, is_enable: bool, db: Session = Depends(get_db),
                         Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.pm.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if current_user.level < AuthorityLevel.engineer.value:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return set_user_enable(db, user_id, is_enable)


# 刪除 user
@router.delete("/user")
def delete_a_user(user_id: int,
                  db: Session = Depends(get_db),
                  Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if not check_level(current_user, AuthorityLevel.pm.value):
        raise HTTPException(status_code=401, detail="Unauthorized")

    be_deleted_user = check_user_exist(db, user_id)
    if not be_deleted_user:
        raise HTTPException(status_code=400, detail="User doesn't exist")

    if be_deleted_user.level <= current_user.level:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return delete_user_by_user_id(db, be_deleted_user.id)


#######################################################################################################################
# 創建 root
@router.post("/user/root", response_model=UserViewModel)
def create_root_and_default_engineer(user_data: UserCreateModel, db: Session = Depends(get_db)):
    check_root_exist(db)
    if check_root_exist(db):
        raise HTTPException(status_code=400, detail="root already exist")
    user_db = create_user(db, user_data)

    # create a default user for principle engineer
    create_user(db, UserCreateModel(
        level=AuthorityLevel.default_engineer.value,
        email="default_engineer@fastwise.net",
        password=user_data.password,
        name="default_engineer",
        status=UserStatus.online,
        info={}
    ))
    return user_db
