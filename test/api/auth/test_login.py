from test.main import client


def test_login_success():
    response = client.post("/auth/login", json={
        "email": "pm@fastwise.net",
        "password": "pm"
    })
    assert response.status_code == 200
    result = response.json()
    assert "User" in result
    assert "is_enable" in result
    assert "access_token" in result
    assert "refresh_token" in result
    assert "token_type" in result
    assert result["User"]["email"] == "pm@fastwise.net"


def test_login_incorrect_credentials():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "incorrect"
    })
    assert response.status_code == 401
    result = response.json()
    assert "detail" in result
    assert result["detail"] == "Incorrect email or password"


def test_login_user_not_enabled():
    response = client.post("/auth/login", json={
        "email": "pm@fastwise.net",
        "password": "root"
    })
    assert response.status_code == 401
    result = response.json()
    assert "detail" in result
    assert result["detail"] == "user 未啟用"


