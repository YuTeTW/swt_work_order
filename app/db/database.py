from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autoflush=False, bind=engine, )
Base = declarative_base()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
