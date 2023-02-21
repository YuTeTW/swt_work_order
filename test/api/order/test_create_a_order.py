import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app, get_db

client = TestClient(app)


def login(email, password) -> str:
    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    return response.json()["access_token"]


def test_create_a_order(db: Session):
    # 測試資料準備
    client_user = User(name="client", level=AuthorityLevel.client.value)
    db.add(client_user)
    db.commit()

    # 登入取得 access token
    access_token = login("", "")

    # 新增一筆工單
    order_create = OrderCreateModel(detail=["test"], file_name=["test.txt"], client_id=client_user.id)
    response = client.post("/order", headers={"Authorization": f"Bearer {access_token}"}, json=order_create)

    # 確認回傳的 HTTP 狀態碼為 200
    assert response.status_code == 200

    # 確認回傳的資料為新增成功的工單
    data = response.json()
    assert "id" in data
    assert data["detail"] == ["test"]
    assert data["file_name"] == ["test.txt"]
    assert data["client_id"] == client_user.id
    assert data["company_name"] == "client"

    # 確認工單已被儲存到資料庫
    order_db = db.query(Order).get(data["id"])
    assert order_db is not None
    assert order_db.detail == ["test"]
    assert order_db.file_name == ["test.txt"]
    assert order_db.client_id == client_user.id
    assert order_db.company_name == "client"


def test_client_does_not_exist(db: Session):
    # 測試當 client_id 找不到時，應該回傳 404
    order_create = {
        "client_id": 9999999999,
        "order_issue_id": 1,
        "description": "開機很久",
        "detail": [
            "問題1",
            "問題2",
            "問題3"
        ]
    }

    # 登入取得 access token
    access_token = login("", "")

    response = client.post("/order", headers={"Authorization": f"Bearer {access_token}"}, json=order_create)
    assert response.status_code == 404


def test_client_create_order_for_other_client(db: Session):
    # 測試當一般使用者嘗試為別人新增工單時，應該回傳 401
    order_create = {
        "client_id": 9999999999,
        "order_issue_id": 1,
        "description": "開機很久",
        "detail": [
            "問題1",
            "問題2",
            "問題3"
        ]
    }

    # 登入取得 access token
    access_token = login("", "")
    response = client.post("/order", headers={"Authorization": f"Bearer {access_token}"}, json=order_create)
    assert response.status_code == 401


def test_create_order_for_pm_or_engineer(db: Session):
    # 測試當 client 嘗試為別人新增工單時，應該回傳 422
    access_token = login(db, "client")
    response = client.post("/order", headers={"Authorization": f"Bearer {access_token}"}, json=order_create)
    assert response.status_code == 422
