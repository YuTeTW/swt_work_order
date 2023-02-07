import os
from datetime import timedelta
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.core.config import HOST_NAME
from app.server.authentication import create_access_token

load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='./templates'
)


# async def send_email_async(subject: str, email_to: str, body: dict):
#     print(subject)
#     print(email_to)
#     print(body)
#     verify_code = body["verify_code"]
#
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=verify_code
#     )
#
#     fm = FastMail(conf)
#     await fm.send_message(message)


# async def send_email_async(email: str, verify_code: str):
#     title = "fasteyes verify Code"
#     template = f"""
#            <html>
#                <body>
#                      <h1>
#                         認證碼：{verify_code}
#                      </h1>
#                </body>
#            </html>
#        """
#     message = MessageSchema(
#         subject=title,
#         recipients=[email],
#         html=template
#     )
#     fm = FastMail(conf)
#     await fm.send_message(message)


def send_email(email: str, background_tasks: BackgroundTasks):
    title = "SWT 工單系統"
    template = f"""
           <html>
               <body>
                     <h1>
                        已建立一則新工單
                     </h1>
               </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        html=template,
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)


#
# def send_email_background(subject: str, email_to: str, body: dict,background_tasks: BackgroundTasks):
#     template = f"""
#            <html>
#                <body>
#                      <h1>
#                         員工編號: {body["serial_number"]}
#                      </h1>
#                      <h2>
#                         員工姓名: {body["name"]}
#                      </h2>
#                      <h2>
#                         員工溫度:{body["observation"]["info"]["temperature"]}
#                      </h2>
#                      <h2>
#                         員工觀測結果:{body["observation"]["id"]}
#                      </h2>
#                     <a href="HOST_NAME/Files/download/image/device/2/file_name/{body["observation"]["image_name"]}" />
#             </body>
#            </html>
#        """
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         subtype="html",
#         html=template
#     )
#
#     fm = FastMail(conf)
#     background_tasks.add_task(
#         fm.send_message, message)


def send_verify_code_email_async(email: str, verify_code: str, background_tasks: BackgroundTasks):
    title = "fasteyes verify Code"
    template = f"""
           <html>
               <body>
                     <h1>
                        認證碼：{verify_code}
                     </h1>
               </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        body=template
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return verify_code


def send_verification_email(email: str, background_tasks: BackgroundTasks):
    token_data = {
        "username": email
    }

    token = create_access_token(token_data)

    template = f"""
        <html>
            <body">
                  <a href="HOST_NAME/auth/verify_email?token={token}">
                  啟用帳號
                  </a>
            </body>
        </html>
    """
    message = MessageSchema(
        subject="Email verification",
        recipients=[email],
        html=template
    )

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return token


def send_forget_password_email(email: str, password: str, background_tasks: BackgroundTasks):
    template = f"""
        <html>
            <body>
                <h1>
                    新密碼：{password}
                </h1>
            </body>
        </html>
    """

    message = MessageSchema(
        subject="forget password",
        recipients=[email],
        html=template
    )

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)


# def send_email_temperature_alert(background_tasks: BackgroundTasks, db: Session, email: str,
#                                  observation_db: FasteyesObservation):
#     title = "溫度異常"
#     staff_db = get_staff_by_id(db, observation_db.staff_id)
#     if staff_db:
#         name = staff_db.info["name"]
#         serial_number = staff_db.serial_number
#     else:
#         name = "Unknow"
#         serial_number = "None"
#
#     # send_email_background(title, email,
#     #                       {'title': title, 'name': name, 'observation': observation_db.to_dict(),
#     #                        'serial_number': serial_number},background_tasks)
#
#     template = f"""
#            <html>
#                <body>
#                      <h1>
#                         員工編號: {serial_number}
#                      </h1>
#                      <h2>
#                         員工姓名: {name}
#                      </h2>
#                      <h2>
#                         員工溫度:{observation_db.info["temperature"]}
#                      </h2>
#                      <h2>
#                         員工觀測結果:{observation_db.id}
#                      </h2>
#                     <a href="{HOST_NAME}/Files/download/image/device/{observation_db.fasteyes_device_id}/file_name/{observation_db.image_name}">
#                     觀測結果圖片
#                     </a>
#             </body>
#            </html>
#        """
#     message = MessageSchema(
#         subject=title,
#         recipients=[email],
#         html=template
#     )
#     fm = FastMail(conf)
#     background_tasks.add_task(
#         fm.send_message, message)


# def send_email_device_alert(background_tasks: BackgroundTasks, email: str,
#                             observation_db: observation, device_db: device):
#     title = "Device異常"
#     template = f"""
#            <html>
#                <body>
#                      <h1>
#                         裝置名稱: {device_db.name}
#                      </h1>
#                      <h2>
#                         裝置編號: {device_db.serial_number}
#                      </h2>
#                      <h2>
#                         裝置位置: {device_db.area}
#                      </h2>
#                      <h2>
#                         溫度:{observation_db.info["temperature"]}
#                      </h2>
#
#                      <h2>
#                         濕度:{observation_db.info["humidity"]}
#                      </h2>
#             </body>
#            </html>
#        """
#     #     < h4 >
#     #     溫度正常範圍: {observation_db.info["alarm_temperature_lower_limit"]}～{
#     #         observation_db.info["alarm_temperature_upper_limit"]}
#     #
#     # < / h4 >
#     # < h4 >
#     # 濕度正常範圍: {observation_db.info["alarm_humidity_lower_limit"]}～{observation_db.info["alarm_humidity_upper_limit"]}
#     # < / h4 >
#     # print(background_tasks)
#     message = MessageSchema(
#         subject=title,
#         recipients=[email],
#         html=template
#     )
#     fm = FastMail(conf)
#     background_tasks.add_task(
#         fm.send_message, message)
#     # print(background_tasks.tasks)


def send_invite_mail(email: str, level: int, group_id: int, background_tasks: BackgroundTasks):
    token_data = {
        "email": email,
        "level": level,
        "group_id": group_id
    }

    token = create_access_token(token_data, expires_delta=timedelta(minutes=999999999))

    title = "fasteyes user 認證信"
    template = f"""
           <html>
               <body>
                     <h1>
                        認證信
                     </h1>
                     <a href="{HOST_NAME}/users/verify/{token}">
                    點此連結完成認證
                    </a>
               </body>
           </html>
       """
    message = MessageSchema(
        subject=title,
        recipients=[email],
        html=template,
        subtype=None
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message)

    return token
