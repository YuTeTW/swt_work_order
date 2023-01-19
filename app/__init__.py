from fastapi import FastAPI, BackgroundTasks
from app.api.api_router import router
from app.db.database import engine, Base
from starlette.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

background_tasks = BackgroundTasks()

Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost:8080",
    "*"
]
# templates = Jinja2Templates(directory="templates")


def create_app():
    app = FastAPI()
    # app.host = "localhost/127.0.0.1"
    # app.port = "8080"
    # app.servers ={"url": "https://localhost/127.0.0.1", "description": "Staging environment"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.include_router(router)
    # app.mount("/static", StaticFiles(directory="static"), name="static")
    add_pagination(app)
    return app
