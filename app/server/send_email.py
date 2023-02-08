import os

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv

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


def send_email(email: str, background_tasks: BackgroundTasks):
    title = "SWT 工單系統"
    template = """
        <html>
            <body>
                <h1 style="text-align:center;">已建立一則新工單</h1>
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

