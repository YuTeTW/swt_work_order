import os
import sys
from dotenv import load_dotenv

p = os.path.abspath('../')
sys.path.insert(1, p)
load_dotenv('.env')
FILE_PATH = os.getcwd() + "/db_image/"
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
SQL_TYPE: int = 1 if SQLALCHEMY_DATABASE_URL.find("postgresql:") > 0 else 0
# SQL_TYPE 0: sqlite , 1: postgresql

