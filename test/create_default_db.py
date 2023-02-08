import os
import random

import requests
import json

path = os.getcwd()
URL = "http://192.168.45.103:8000"


def get_current_user_header():
    with open(path + '/User_data/Headers.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return {"Authorization": "Bearer " + data["access_token"]}


def get_user_data(user):
    # print(path+ '/User_data/')
    with open(os.getcwd() + '/User_data/' + user + '.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def get_uuid_data(uuid):
    with open(path + '/UUID_data/' + uuid + '.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def add_root():
    url = URL + "/user/root"
    root_data = {
        "name": "root",
        "password": "root",
        "email": "root@fastwise.net",
        "info": {
            "telephone_number": "0987654321",
            "line_id": "@kadiggec",
            "note": "nothing",
            "office_hours": "8AM-6PM"
        }
    }
    response = requests.post(url, json=root_data)
    print(response.json())


def Login_root():
    url = URL + "/auth/login"
    login_data = {
        "email": "root@fastwise.net",
        "password": "root"
    }
    response = requests.post(url, data=json.dumps(login_data))
    with open(path + '/User_data/Headers.json', 'w', encoding='utf-8') as outfile:
        json.dump(response.json(), outfile)


def add_user():
    url = URL + "/user/create"
    for pm_name in ["alice", "chingwei", "peter"]:
        user_data = {
            "name": pm_name,
            "password": pm_name,
            "email": pm_name + "@fastwise.net",
            "info": {
                "telephone_number": "0987654321",
                "line_id": "@kadiggec",
                "note": "nothing",
                "office_hours": "8AM-6PM"
            }
        }
        response = requests.post(url, params={"level": 1}, json=user_data, headers=get_current_user_header())
        print(response.json())
    for engineer_name in ["kenny", "tim", "fang", "ricky", "dave"]:
        user_data = {
            "name": engineer_name,
            "password": engineer_name,
            "email": engineer_name + "@fastwise.net",
            "info": {
                "telephone_number": "0987654321",
                "line_id": "@kadiggec",
                "note": "nothing",
                "office_hours": "8AM-6PM"
            }
        }
        response = requests.post(url, params={"level": 2}, json=user_data, headers=get_current_user_header())
        print(response.json())
    for i in range(10):
        user_data = {
            "name": "client_" + str(i),
            "password": "client" + str(i),
            "email": "client" + str(i) + "@fastwise.net",
            "info": {
                "telephone_number": "0987654321",
                "line_id": "@kadiggec",
                "note": "nothing",
                "office_hours": "8AM-6PM"
            }
        }
        response = requests.post(url, params={"level": 3}, json=user_data, headers=get_current_user_header())
        print(response.json())


# def add_user():
#     url = URL + "/user/create"
#     user_types = [
#     ("pm", ["alice", "chingwei", "peter"]),
#     ("engineer", ["kenny", "tim", "fang", "ricky", "dave"]),
#     ("client", [f"client_{i}" for i in range(10)])
#     ]
#     for user_type, names in user_types:
#         for name in names:
#             user_data = {
#                 "name": name,
#                 "password": name,
#                 "email": f"{name}@fastwise.net",
#                 "info": {
#                     "telephone_number": "0987654321",
#                     "line_id": "@kadiggec",
#                     "note": "nothing",
#                     "office_hours": "8AM-6PM"
#                 }
#             }
#             level = 1 if user_type == "pm" else 0
#             response = requests.post(url, params={"level": level}, json=user_data, headers=get_current_user_header())
#             print(response.json())


def create_order_issue():
    url = URL + "/order_issue"
    issue = ["電腦故障", "伺服器無回應", "網路斷線", "作業系統問題", "mail server問題"]
    for issue_name in issue:
        department_data = {
            "name": issue_name,
            "severity": 1,
            "time_hours": 10
        }
        rsp = requests.post(url, json=department_data, headers=get_current_user_header())
        print(rsp.json())


def create_order():
    url = URL + "/order"
    for client_id in range(10, 20):
        for problem in range(5):
            issue = ["電腦故障", "伺服器無回應", "網路斷線", "作業系統問題", "mail server問題"]
            order_issue_id = random.randint(1, 5)
            serial_number = str(client_id) + "-" + str(problem)
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
            rsp = requests.post(url, params={"client_id": client_id}, json=order_data,
                                headers=get_current_user_header())
            print(rsp.json())


def create_order_message():
    url = URL + "/order_message"
    for order_id in range(1, 51):
        for message in ["第一次修改", "第二次修改", "第三次修改"]:
            order_data = {
                "order_id": order_id,
                "message": message,
            }
            rsp = requests.post(url, params={"user_id": random.randint(5, 10)}, json=order_data,
                                headers=get_current_user_header())
            print(rsp.json())


if __name__ == '__main__':
    add_root()
    Login_root()
    add_user()
    create_order_issue()
    create_order()
    create_order_message()
