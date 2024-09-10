import os
from pathlib import Path
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from dotenv import load_dotenv
from pydantic import DirectoryPath
load_dotenv('.env')

class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = 587
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=str(Envs.MAIL_USERNAME),
    MAIL_PASSWORD=str(Envs.MAIL_PASSWORD),
    MAIL_FROM=str(Envs.MAIL_FROM),
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=str(Envs.MAIL_SERVER),
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates'
)

async def send_email_background(
        background_tasks: BackgroundTasks,
        recipients: list,
        subject: str,
        context: dict,
        template_name: str
):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    background_tasks.add_task(
       fm.send_message, message, template_name=template_name)


