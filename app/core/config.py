import os
import sys
from dotenv import load_dotenv

p = os.path.abspath('../')
sys.path.insert(1, p)
PAGE_SIZE = 5
load_dotenv('.env')
FILE_PATH = os.getcwd() + "/db_image/"
HOST_NAME = os.getenv('HOST_NAME')
SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
SQL_TYPE: int = 1 if SQLALCHEMY_DATABASE_URL.find("postgresql:") > 0 else 0
# SQL_TYPE 0: sqlite , 1: postgresql
FASTEYES_OUTPUT_PATH = os.getenv('FASTEYES_OUTPUT_PATH')

