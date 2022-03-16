from peewee import *
import datetime
import config

now = datetime.datetime.now

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
    name = TextField(column_name="name", unique=True)
    surname = TextField(column_name="surname", unique=True)
    password = TextField(column_name="password", null=True)
    salt = TextField(column_name="salt", null=True)
    photo = TextField(column_name="photo", null=True)
    username = TextField(column_name="username", unique=True, null=True)
    statusId = IntegerField(column_name="status_id", null=True)
    registrationTime = DateTimeField(column_name="registration_time", default=now)
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


class News(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    title = TextField(column_name="title")
    body = TextField(column_name="body")
    statusId = IntegerField(column_name="status_id", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    updateTime = DateTimeField(column_name="update_time", null=True)

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
