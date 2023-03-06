from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks

from app.db.database import get_db
from app.helper.authentication import authorize_user
from app.server.send_email import send_forget_password_email
from app.server.user.crud import check_email_exist
from app.server.authentication.crud import create_and_set_user_password
from app.server.authentication import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, AuthorityLevel,
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

        return {"User": user, "is_enable": user.is_enable, "access_token": access_token,
                "refresh_token": refresh_token, "token_type": "bearer"}


# 忘記密碼寄信
@router.post("/auth/forget_password")
def forget_password(send_to_email: str, forget_account: str, background_tasks: BackgroundTasks,
                    Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    current_user = authorize_user(Authorize, db)

    if current_user.level > AuthorityLevel.pm.value:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not check_email_exist(db, forget_account):
        return "Account is not exist"

    password = create_and_set_user_password(db, forget_account)
    send_forget_password_email(send_to_email, password, background_tasks=background_tasks)
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


@router.post("/auth/adlogin")
def ad_login():
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, RedirectResponse
    import requests
    import uuid

    app = FastAPI()

    # Microsoft AD 設定
    TENANT_ID = 'e2162208-310c-42ac-943e-8fafed5bc442'
    CLIENT_ID = 'f36ddc8f-4f9c-4a38-97d2-019b70a7497f'
    CLIENT_SECRET = '7NS8Q~QKItyTsIbVk3pLmw0UO1zNQchC5mzR.bLz'
    SCOPE = 'User.ReadBasic.All'
    URI = 'http://localhost:5000/getAToken'

    @app.get('/')
    async def index(request: Request):
        # 檢查是否已經驗證
        if 'access_token' in request.cookies:
            access_token = request.cookies.get('access_token')
            # 使用驗證過的 access token 請求使用者資料
            user_response = requests.get('https://graph.microsoft.com/v1.0/me', headers={'Authorization': f'Bearer {access_token}'})
            user_data = user_response.json()
            return {'message': f'Hello {user_data}'}
        else:
            # 產生隨機狀態碼
            state = str(uuid.uuid4())
            # 將 state 存入 cookies
            response = RedirectResponse(url=f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={URI}&response_mode=query&scope={SCOPE}&state={state}')
            response.set_cookie(key='state', value=state)
            return response

    @app.get('/getAToken')
    async def get_access_token(request: Request, code: str, state: str):
        # 檢查 state 是否相符
        if state != request.cookies.get('state'):
            return {'message': 'Invalid state'}
        else:
            # 請求 access token
            token_response = requests.post(f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token', data={
                'grant_type': 'authorization_code',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': code,
                'redirect_uri': URI
            })
            token_data = token_response.json()
            # 存入 access token
            response = RedirectResponse(url='/')
            response.set_cookie(key='access_token', value=token_data['access_token'])
            return response


