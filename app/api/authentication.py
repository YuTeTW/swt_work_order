from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks
from app.db.database import get_db
from app.helper.authentication import authorize_user
# from app.server.send_email import send_forget_password_email
from app.server.user.crud import check_email_exist
from app.server.authentication.crud import create_and_set_user_password
from app.server.authentication import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.models.schemas.user import (
    UserLoginViewModel,
    UserViewModel,
    LoginResultUserViewModel
)

router = APIRouter()


@router.get("/")
def version():
    return {"Program": "SWT-Work-Order", "Version": "1.0.1"}


# 登入
@router.post("/auth/login", response_model=LoginResultUserViewModel)
def login(user_data: UserLoginViewModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(user_data.email, user_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token = Authorize.create_access_token(subject=user.email, expires_time=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token = Authorize.create_refresh_token(subject=user.email)

        return {"User": user, "Status": user.is_enable, "access_token": access_token,
                "refresh_token": refresh_token, "token_type": "bearer"}


# 忘記密碼寄信
@router.post("/auth/forget_password")
def forget_password(background_tasks: BackgroundTasks,
                    email: str, db: Session = Depends(get_db)):
    if not check_email_exist(db, email):
        return "Email is not exist"

    password = create_and_set_user_password(db, email)

    send_forget_password_email(email, password, background_tasks=background_tasks)
    return "Send forget password email done"


# 取得登入User
@router.post("/auth/pingServer", response_model=UserViewModel)
def ping_server(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = authorize_user(Authorize, db)
    return current_user


# 更新 token
@router.post('/auth/refresh')
def refresh_token(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}
