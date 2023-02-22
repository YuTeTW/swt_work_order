# import jpype

from app import create_app
from app.db.database import get_db
from app.models.domain.Error_handler import ErrorHandler, UnicornException
from starlette.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import Request
app = create_app()


# @app.on_event("startup")
# def startup_event():
#     jpype.startJVM()
#
# @app.on_event("shutdown")
# def shutdown_event():
#     jpype.shutdownJVM()


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # 紀錄到Table
    db = next(get_db())
    db.begin()
    db_Error_handler = ErrorHandler(name=exc.name,
                                    description=exc.description,
                                    status_code=exc.status_code)
    db.add(db_Error_handler)
    db.commit()
    db.refresh(db_Error_handler)
    return JSONResponse(
        status_code=exc.status_code,
        content={"function_name": exc.name,
                 "description": exc.description}
    )


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(exc: AuthJWTException):
    # 紀錄到Table
    db = next(get_db())
    db.begin()
    db_Error_handler = ErrorHandler(name="AuthJWTException",
                                    description=exc.message,
                                    status_code=exc.status_code)
    db.add(db_Error_handler)
    db.commit()
    db.refresh(db_Error_handler)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# uvicorn app.main:app --host 192.168.45.83 --port 8080 --reload
