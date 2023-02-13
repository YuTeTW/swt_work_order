from fastapi import APIRouter, Depends, HTTPException
from typing import List
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.authentication import AuthorityLevel, verify_password, check_level
from app.server.authentication.crud import set_user_enable
from app.server.user.crud import (
    create_user,
    get_user_by_email,
    get_all_users,
    modify_user,
    modify_user_password,
    delete_user_by_user_id,
    check_root_exist,
    check_user_exist,
    get_user_by_id
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
    if user_create.level > AuthorityLevel.client.value or user_create.level < AuthorityLevel.root.value:
        raise HTTPException(status_code=405, detail="Method Not Allowed")

    if current_user.level >= user_create.level or current_user.level >= 2:
        raise HTTPException(status_code=401, detail="Unauthorized")

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
        raise HTTPException(status_code=401, detail="Unauthorized")

    return get_all_users(db)


# user id 修改 User Info
@router.patch("/user/info", response_model=UserViewModel)
def patch_user_info(user_patch: UserPatchInfoModel,
                    db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    current_user = authorize_user(Authorize, db)
    if current_user.level >= user_patch.level or current_user.level > AuthorityLevel.pm.value:
        raise HTTPException(status_code=401, detail="Unauthorized")
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
    if user_id < AuthorityLevel.engineer.value:
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
def create_root(user_data: UserCreateModel, db: Session = Depends(get_db)):
    check_root_exist(db)
    if check_root_exist(db):
        raise HTTPException(status_code=400, detail="root already exist")
    user_db = create_user(db, user_data)

    return user_db
