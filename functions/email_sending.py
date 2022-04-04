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
        html = message_text
        message.attach(MIMEText(html, "html"))
        server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port)
        server.login(email_smtp_login, email_smtp_password)
        server.send_message(message)
        server.quit()
        Email_message.create(
            smtpEmail=str(email_smtp_login),
            recipient=str(recipient),
            subject=str(subject),
            body=str(html),
            date=datetime.now()
        )
        return True
    except Exception as error:
        error_description = "Адрес: \"" + str(recipient) + "\" на тему: \"" + str(subject) + "\""
        error_log(error, error_description, "Отправка Email")
        return False


def send_welcome_message(recipient, subject, email_token, name, surname):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    html = """
    <html>
        <body>
            <p>
                <b>
                    Регистрация успешна    
                </b>
                <br>
                Здравствуйте, {name} {surname}!
                <br>
                Благодарим за регистрацию на нашем сервисе.
                <br>
                <br>
                Ваш логин {email}
                <br>
                <br>
                <a href={url}>Подтвердите почтовый адрес</a>
                <br>
                <br>
                С уважением octo global.
            </p>
        </body>
    </html>
    """.format(name=name, surname=surname, email=recipient, url=url)
    return send_email(recipient, subject, html)


def send_verification_message(recipient, subject, email_token, name, surname):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        <a href={url}>Подтвердите почтовый адрес</a>
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, email=recipient, url=url)
    return send_email(recipient, subject, html)


def send_recovery_message(recipient, subject, time, token, name, surname):
    query_string = str(urlencode(OrderedDict(token=token, expaire=str(time))))
    url = str(config.front_domain + "/reset_password?" + query_string)
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Для изменения пароля нажмите на ссылку ниже:
                        <br>
                        <br>
                        <a href={url}>Восстановить пароль</a>
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, email=recipient, url=url)
    return send_email(recipient, subject, html)
