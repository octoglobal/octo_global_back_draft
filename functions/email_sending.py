import smtplib
from datetime import datetime
from urllib.parse import urlencode
from collections import OrderedDict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
# import mimetypes
# from email import encoders
# from email.mime.base import MIMEBase
# from email.mime.image import MIMEImage
# from email.mime.audio import MIMEAudio
import config
from database import Email_message, Notification
from functions.loger import error_log


def send_email(recipient_id, recipient, subject, message_text):
    Notification.create(
        recipient_id=int(recipient_id),
        recipient_email=str(recipient),
        subject=str(subject),
        body=str(message_text),
        date=datetime.now()
    )
    try:
        email_smtp_login = config.smtp_login
        email_smtp_password = config.smtp_password
        message = MIMEMultipart()
        message["From"] = formataddr(("OctoGlobal", config.smtp_from))
        # message["From"] = config.smtp_from
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


def send_welcome_message(recipient_id, recipient, subject, email_token, name, surname):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    html = """
    <html>
        <body>
            <p>
                <b>
                    Регистрация успешно завершена.    
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
    return send_email(recipient_id, recipient, subject, html)


def send_verification_message(recipient_id, recipient, subject, email_token, name, surname):
    query_string = str(urlencode(OrderedDict(email=recipient, token=email_token)))
    url = str(config.front_domain + "/confirm?" + query_string)
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Подтвердите почтовый адрес
                        <br>
                        <br>
                        <a href={url}>Подтвердить</a>
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, email=recipient, url=url)
    return send_email(recipient_id, recipient, subject, html)


def send_recovery_message(recipient_id, recipient, subject, time, token, name, surname):
    query_string = str(urlencode(OrderedDict(token=token, expaire=str(time))))
    url = str(config.front_domain + "/reset_password?" + query_string)
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Вы отправили запрос на восстановление пароля от почтового ящика.
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
    return send_email(recipient_id, recipient, subject, html)


def send_add_balance(recipient_id, recipient, subject, user):
    if user["phone"]:
        html = """
                <html>
                    <body>
                        <p>
                            Заявка на пополнение счета.
                            <br>
                            <br>
                            Пользователь:
                            <br>
                            <br>
                            ФИ: {user_surname} {user_name}
                            <br>
                            ID: {user_long_id}
                            <br>
                            Email: {user_email}
                            <br>
                            Телефон: {user_phone}
                        </p>
                    </body>
                </html>
                """.format(user_surname=user["name"], user_name=user["surname"], user_long_id=user["personalAreaId"],
                           user_email=user["email"], user_phone=user["phone"])
    else:
        html = """
                <html>
                    <body>
                        <p>
                            Заявка на пополнение счета.
                            <br>
                            <br>
                            Пользователь:
                            <br>
                            <br>
                            ФИ: {user_surname} {user_name}
                            <br>
                            ID: {user_long_id}
                            <br>
                            Email: {user_email}
                        </p>
                    </body>
                </html>
                """.format(user_surname=user["name"], user_name=user["surname"], user_long_id=user["personalAreaId"],
                           user_email=user["email"])
    return send_email(recipient_id, recipient, subject, html)


def send_order_return(recipient_id, recipient, subject, user, order):
    html = """
            <html>
                <body>
                    <p>
                        Заявка на возврат товара.
                        <br>
                        <br>
                        Пользователь:
                        <br>
                        <br>
                        ФИ: {user_surname} {user_name}
                        <br>
                        ID: {user_long_id}
                        <br>
                        Email: {user_email}
                        <br>
                        <br>
                        Заказ:
                        <br>
                        <br>
                        Track: {order_track}
                        <br>
                        ID: {order_long_id}
                    </p>
                </body>
            </html>
            """.format(user_surname=user["name"], user_name=user["surname"], user_long_id=user["personalAreaId"],
                       user_email=user["email"], order_track=order["trackNumber"], order_long_id=order["longId"])
    return send_email(recipient_id, recipient, subject, html)


def send_order_check(recipient_id, recipient, subject, user, order):
    html = """
            <html>
                <body>
                    <p>
                        Заявка на проверку товара.
                        <br>
                        <br>
                        Пользователь:
                        <br>
                        <br>
                        ФИ: {user_surname} {user_name}
                        <br>
                        ID: {user_long_id}
                        <br>
                        Email: {user_email}
                        <br>
                        <br>
                        Заказ:
                        <br>
                        <br>
                        Track: {order_track}
                        <br>
                        ID: {order_long_id}
                    </p>
                </body>
            </html>
            """.format(user_surname=user["name"], user_name=user["surname"], user_long_id=user["personalAreaId"],
                       user_email=user["email"], order_track=order["trackNumber"], order_long_id=order["longId"])
    return send_email(recipient_id, recipient, subject, html)


def send_registration_of_the_parcel(recipient_id, recipient, subject, user, package, address):
    html = """
            <html>
                <body>
                    <p>
                        Заявка на отправку посылки.
                        <br>
                        <br>
                        Пользователь:
                        <br>
                        <br>
                        ФИ: {user_surname} {user_name}
                        <br>
                        ID: {user_long_id}
                        <br>
                        Email: {user_email}
                        <br>
                        <br>
                        Посылка:
                        <br>
                        <br>
                        ID: {package_long_id}
                        <br>
                        <br>
                        Данные для отправки:
                        <br>
                        <br>
                        Адрес: {address_string}
                        <br>
                        ФИ: {address_surname} {address_name}
                        <br>
                        телефон: {address_phone}
                    </p>
                </body>
            </html>
            """.format(user_surname=user["name"], user_name=user["surname"], user_long_id=user["personalAreaId"],
                       user_email=user["email"], package_long_id=package["longId"],
                       address_string=address["address_string"], address_name=address["name"],
                       address_surname=address["surname"], address_phone=address["phone"])
    return send_email(recipient_id, recipient, subject, html)


def send_arrived_at_the_warehouse(recipient_id, recipient, subject, name, surname, order_number):
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Сообщаем Вам о том, что Ваш заказ № {order_number} пришел на склад
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, order_number=order_number)
    return send_email(recipient_id, recipient, subject, html)


def send_cancelled_package(recipient_id, recipient, subject, name, surname, package_number):
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Консолидация Вашей посылки № {package_number} отменена администратором. 
                        Для того, чтобы получить подробную информацию об отмене, свяжитесь с нами по почте
                        help@octo.global
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, package_number=package_number)
    return send_email(recipient_id, recipient, subject, html)


def send_delete_package(recipient_id, recipient, subject, name, surname, package_number):
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Ваша посылка № {package_number} удалена администратором. 
                        Для того, чтобы получить подробную информацию об отмене, свяжитесь с нами по почте
                        help@octo.global
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, package_number=package_number)
    return send_email(recipient_id, recipient, subject, html)


def send_package_send(recipient_id, recipient, subject, name, surname, package_number, package_address):
    html = """
            <html>
                <body>
                    <p>
                        Здравствуйте, {name} {surname}!
                        <br>
                        <br>
                        Ваша посылка № {package_number} отправлена в Россию по адресу:
                        {package_address} 
                        <br>
                        <br>
                        С уважением octo global.
                    </p>
                </body>
            </html>
            """.format(name=name, surname=surname, package_number=package_number, package_address=package_address)
    return send_email(recipient_id, recipient, subject, html)


def send_feedback(recipient_id, recipient, subject, email, question):
    html = """
            <html>
                <body>
                    <p>
                        Вопрос от посетителя:
                        <br>
                        <br>
                        Email для обратной связи:
                        <br>
                        {email}
                        <br>
                        <br>
                        Вопрос:
                        <br>
                        {question}
                    </p>
                </body>
            </html>
            """.format(email=email, question=question)
    return send_email(recipient_id, recipient, subject, html)
