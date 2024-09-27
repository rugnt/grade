import smtplib

from app.logger import logger
from celery import shared_task
from app.config import settings

from email.message import EmailMessage
from celery import Celery
from celery.schedules import crontab

includes_celery = ['app.tasks']
celery_app = Celery('app', broker="redis://redis:6379/1", include=includes_celery)


@celery_app.task
def send_email_message(text: str, email_addr: str):
    try:
        email = EmailMessage()
        email['Subject'] = 'Добавлена новая книга'
        email['From'] = settings.SMTP_USER
        email['To'] = email_addr

        email.set_content(
            text,
            subtype='plain'
        )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email)
    except Exception as e:
        logger.exception(f'Ошибка при отправке на почту {email_addr}', exc_info=e)



