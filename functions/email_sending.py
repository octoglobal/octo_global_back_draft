import smtplib
from datetime import datetime
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
import config
from database import Email_message
from functions.loger import error_log


def send_email(recipient, subject, message_text):
    try:
        email_smtp_login = config.email_smtp_login
        email_smtp_password = config.email_smtp_password
        message = MIMEMultipart()
        message["From"] = email_smtp_login
        message["To"] = str(recipient)
        message["Subject"] = str(subject)
        text = message_text
        message.attach(MIMEText(text, "plain"))
        server = smtplib.SMTP_SSL("smtp.mail.ru", 465)
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
    text = "Приветствие бла бла" \
           "\n\nДля подтверждения почты: " \
           "\n\nСсылка = " + config.front_domain + "/confirm?email=" + str(recipient) + "&token=" + str(email_token)
    return send_email(recipient, subject, text)


def send_verification_message(recipient, subject, email_token):
    text = "Для подтверждения почты: " \
           "\n\nСсылка = " + config.front_domain + "/confirm?email=" + str(recipient) + "&token=" + str(email_token)
    return send_email(recipient, subject, text)


def send_recovery_message(recipient, subject, time, token):
    text = "Для смены пароля: " \
           "\n\nПароль можно сменить до: " + str(time) + \
           "\n\nЗдесь будет query: token = " + str(token)
    return send_email(recipient, subject, text)
