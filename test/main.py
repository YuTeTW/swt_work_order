from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# pytest
# -v 列出各測試完整結果
# -s 輸出函數中print語句
