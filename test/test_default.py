from test.main import client
import os
import random
import time

import requests
import json

path = os.getcwd()
# URL = "http://192.168.45.103:8000"  # Dave Windows

URL = "http://192.168.45.51:8000"  # Dave Mac


def get_current_user_header():
    with open(path + '/test/Headers.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return {"Authorization": "Bearer " + data["access_token"]}


def add_root():
    url = URL + "/user/root"
    root_data = {
        "name": "root",
        "password": "root",
        "email": "root@fastwise.net",
        "level": 0,
        "status": 1,
        "info": {
            "contact_email": "root@fastwise.net",
            "telephone_number": "0987654321",
            "line_id": f"@root000",
            "note": "nothing",
        }
    }
    client.post(url, json=root_data)


def Login_root():
    url = URL + "/auth/login"
    login_data = {
        "email": "root@fastwise.net",
        "password": "root"
    }
    response = client.post(url, data=json.dumps(login_data))
    with open(path + '/test/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)


def add_user():
    url = URL + "/user/create"
    user_types = [
        ("pm", ["pm"]),
        ("engineer", ["engineer"]),
        ("client", ["client"]),
        ("test_is_not_enable", ["test_is_not_enable"])
    ]
    for user_type, names in user_types:
        for name in names:
            user_data = {
                "name": name,
                "password": name,
                "email": f"{name}@fastwise.net",
                "status": 1,
                "info": {
                    "contact_email": f"{name}@fastwise.net",
                    "telephone_number": "0987654321",
                    "line_id": f"@{name}000",
                    "note": "nothing"
                }
            }
            level = 1 if user_type == "pm" else 2 if user_type == "engineer" else 3
            user_data["level"] = level
            client.post(url, json=user_data, headers=get_current_user_header())


def a_user_is_not_enable():
    url = URL + "/user/all"
    rsp = client.get(url, headers=get_current_user_header())
    result = filter(lambda x: x['email'] == 'test_is_not_enable@fastwise.net', rsp.json())
    result = list(result)
    user_id = result[0]["id"]
    url = URL + "/user/is_enable"
    client.patch(url, params={"is_enable": False, "user_id": user_id}, headers=get_current_user_header())


def create_order_issue():
    url = URL + "/order_issue"
    issue = ["電腦故障", "伺服器無回應", "網路斷線", "作業系統問題", "mail server問題"]
    for issue_name in issue:
        department_data = {
            "name": issue_name,
            "severity": random.randint(0, 2),
            "time_hours": random.choice(range(4, 24, 2))
        }
        rsp = client.post(url, json=department_data, headers=get_current_user_header())
        print(rsp.json())


def create_order():
    url = URL + "/order"
    order_id = 1
    for client_id in range(10, 20):
        for problem in range(5):
            issue = ["電腦故障", "伺服器無回應", "網路斷線", "作業系統問題", "mail server問題"]
            order_issue_id = random.randint(1, 5)
            serial_number = f"{client_id}-{problem}"
            order_data = {
                "order_issue_id": order_issue_id,
                "serial_number": serial_number,
                "description": issue[order_issue_id - 1],
                "detail": [
                    "問題1",
                    "問題2",
                    "問題3"
                ]
            }
            rsp = client.post(url, params={"client_id": client_id}, json=order_data,
                                headers=get_current_user_header())
            # time.sleep(1)
            if order_id % 2 == 0:
                rsp = client.patch(URL + "/order/principal",
                                     params={"order_id": order_id,
                                             "engineer_id": random.randint(5, 10)},
                                     headers=get_current_user_header())
            if order_id % 3 == 0:
                rsp = client.patch(URL + "/order/status",
                                     params={"order_id": order_id,
                                             "status": 2},
                                     headers=get_current_user_header())
            order_id += 1


def create_order_message():
    url = URL + "/order_message"
    for order_id in range(1, 51):
        for message in ["第一次修改", "第二次修改", "第三次修改"]:
            order_data = {
                "user_id": random.randint(5, 10),
                "order_id": order_id,
                "message": message,
            }
            rsp = client.post(url, json=order_data, headers=get_current_user_header())
            print(rsp.json())


def teet_default_create():
    add_root()
    Login_root()
    add_user()
    a_user_is_not_enable()
    create_order_issue()
    create_order()
    create_order_message()


teet_default_create()
