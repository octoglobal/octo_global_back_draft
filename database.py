from peewee import *
import config

db = PostgresqlDatabase(
    database=config.db_name,
    user=config.db_user,
    password=config.db_password,
    host=config.db_host,
    port=config.db_port,
    autocommit=True,
    autorollback=True
)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    email = TextField(column_name="email", unique=True)
    phone = TextField(column_name="phone", null=True)
    verifiedEmail = BooleanField(column_name="verified_email")
    name = TextField(column_name="name")
    surname = TextField(column_name="surname")
    password = TextField(column_name="password", null=True)
    salt = TextField(column_name="salt", null=True)
    email_token = TextField(column_name="email_token", null=True)
    photo = TextField(column_name="photo", null=True)
    username = TextField(column_name="username", null=True)
    statusId = IntegerField(column_name="status_id")
    registrationTime = DateTimeField(column_name="registration_time", null=True)
    lastLoginTime = DateTimeField(column_name="last_login_time", null=True)
    deletedTime = DateTimeField(column_name="deleted_time", null=True)

    class Meta:
        table_name = "users"


class Order(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    trackNumber = TextField(column_name="track_number")
    statusId = IntegerField(column_name="status_id", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)

    class Meta:
        table_name = "orders"


class Users_addresses(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    userId = IntegerField(column_name="user_id", null=True)
    address = TextField(column_name="address", null=True)
    delete = BooleanField(column_name="delete", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    deletedTime = DateTimeField(column_name="deleted_time", null=True)

    class Meta:
        table_name = "users_addresses"


class News(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    title = TextField(column_name="title")
    body = TextField(column_name="body")
    statusId = IntegerField(column_name="status_id", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    editedTime = DateTimeField(column_name="edited_time", null=True)

    class Meta:
        table_name = "news"


class Shop(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    title = TextField(column_name="title")
    description = TextField(column_name="description")
    photo = TextField(column_name="photo", null=True)
    priceId = IntegerField(column_name="price_id", null=True)
    url = TextField(column_name="url", null=True)

    class Meta:
        table_name = "shops"


class Email_message(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    smtpEmail = TextField(column_name="smtp_email", null=True)
    recipient = TextField(column_name="recipient", null=True)
    subject = TextField(column_name="subject", null=True)
    body = TextField(column_name="body", null=True)
    date = DateTimeField(column_name="date", null=True)

    class Meta:
        table_name = "email_messages"


class Error(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    error = TextField(column_name="error", null=True)
    description = TextField(column_name="description", null=True)
    source = TextField(column_name="source", null=True)
    date = DateTimeField(column_name="date", null=True)

    class Meta:
        table_name = "errors"
