import smtplib
from datetime import datetime
from urllib.parse import urlencode
from collections import OrderedDict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import mimetypes
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.image import MIMEImage
# from email.mime.audio import MIMEAudio
import config
from database import Email_message
from functions.loger import error_log


def send_email(recipient, subject, message_text):
    try:
        email_smtp_login = config.smtp_login
        email_smtp_password = config.smtp_password
        message = MIMEMultipart()
        message["From"] = config.smtp_from
        message["To"] = str(recipient)
        message["Subject"] = str(subject)
        text = message_text
        message.attach(MIMEText(text, "plain"))
        server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port)
        server.login(email_smtp_login, email_smtp_password)
        server.send_message(message)
        server.quit()
        Email_message.create(
            smtpEmail=str(email_smtp_login),
            recipient=str(recipient),
            subject=str(subject),
            body=str(text),
            date=datetime.now()
        )
        return True
    except Exception as error:
        error_description = "Адрес: \"" + str(recipient) + "\" на тему: \"" + str(subject) + "\""
        error_log(error, error_description, "Отправка Email")
        return False


def send_welcome_message(recipient, subject, email_token):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    text = "Приветствие бла бла" \
           "\n\nДля подтверждения почты: " \
           "\n\nСсылка = " + url
    return send_email(recipient, subject, text)


def send_verification_message(recipient, subject, email_token):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    text = "Для подтверждения почты: " \
           "\n\nСсылка = " + url
    return send_email(recipient, subject, text)


def send_recovery_message(recipient, subject, time, time_string, token):
    query_string = str(urlencode(OrderedDict(token=token, expaire=str(time))))
    url = str(config.front_domain + "/reset_password?" + query_string)
    text = "Для смены пароля: " \
           "\n\nПароль можно сменить до: " + str(time_string) + \
           "\n\nДля смены пароля: " \
           "\n\nСсылка = " + url
    return send_email(recipient, subject, text)
