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
    personalAreaId = IntegerField(column_name="personal_area_id", unique=True)
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
    balance = BigIntegerField(column_name="balance", null=True)

    class Meta:
        table_name = "users"


class Order(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    longId = IntegerField(column_name="long_id", unique=True)
    userId = IntegerField(column_name="user_id")
    packageId = IntegerField(column_name="package_id", null=True)
    title = TextField(column_name="title", null=True)
    comment = TextField(column_name="comment", null=True)
    trackNumber = TextField(column_name="track_number")
    statusId = IntegerField(column_name="status_id", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    approvalTime = DateTimeField(column_name="approval_time", null=True)
    declineTime = DateTimeField(column_name="decline_time", null=True)
    addingToPackageTime = DateTimeField(column_name="adding_to_package_time", null=True)
    invoice_check = BooleanField(column_name="invoice_check", null=True)

    class Meta:
        table_name = "orders"


class Package(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    longId = IntegerField(column_name="long_id", unique=True)
    userId = IntegerField(column_name="user_id")
    addressId = IntegerField(column_name="address_id", null=True)
    statusId = IntegerField(column_name="status_id", null=True)
    # title = TextField(column_name="title", null=True)
    # comment = TextField(column_name="comment", null=True)
    trackNumber = TextField(column_name="track_number", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    agreementToConsolidationTime = DateTimeField(column_name="agreement_to_consolidation_time", null=True)
    dispatchTime = DateTimeField(column_name="dispatch_time", null=True)
    arrivalTime = DateTimeField(column_name="arrival_time", null=True)

    class Meta:
        table_name = "packages"


class Users_addresses(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    userId = IntegerField(column_name="user_id")
    phone = TextField(column_name="phone")
    name = TextField(column_name="name")
    surname = TextField(column_name="surname")
    address_string = TextField(column_name="address_string")
    latitude = TextField(column_name="latitude", null=True)
    longitude = TextField(column_name="longitude", null=True)
    delete = BooleanField(column_name="delete", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    deletedTime = DateTimeField(column_name="deleted_time", null=True)

    class Meta:
        table_name = "users_addresses"


class Users_balance_history(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    userId = IntegerField(column_name="user_id")
    amount = BigIntegerField(column_name="amount")
    comment = TextField(column_name="comment", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)

    class Meta:
        table_name = "users_balance_history"


class Post(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    title = TextField(column_name="title")
    body = TextField(column_name="body")
    statusId = IntegerField(column_name="status_id", null=True)
    createdTime = DateTimeField(column_name="created_time", null=True)
    editedTime = DateTimeField(column_name="edited_time", null=True)

    class Meta:
        table_name = "posts"


class Post_product(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    postId = IntegerField(column_name="post_id", null=True)
    title = TextField(column_name="title", null=True)
    body = TextField(column_name="body", null=True)
    photo = TextField(column_name="photo", null=True)
    url = TextField(column_name="url", null=True)

    class Meta:
        table_name = "post_product"


# class Post_photo(BaseModel):
#     id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
#     post_id = IntegerField(column_name="post_id")
#     image_hash = TextField(column_name="image_hash")
#     statusId = IntegerField(column_name="status_id", null=True)
#
#     class Meta:
#         table_name = "post_photo"


class Shop(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    alias = TextField(column_name="alias", unique=True, null=True)
    title = TextField(column_name="title", null=True)
    description = TextField(column_name="description", null=True)
    photo = TextField(column_name="photo", null=True)
    logo = TextField(column_name="logo", null=True)
    url = TextField(column_name="url", null=True)
    rating = IntegerField(column_name="rating", null=True)

    class Meta:
        table_name = "shops"


class Tag(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    title = TextField(column_name="title", unique=True)

    class Meta:
        table_name = "tags"


class Tag_of_shops(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    shop_id = IntegerField(column_name="shop_id")
    tag_id = IntegerField(column_name="tag_id")

    class Meta:
        table_name = "tag_of_shops"


class Review(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    user_id = IntegerField(column_name="user_id")
    text = TextField(column_name="text")
    createdTime = DateTimeField(column_name="created_time", null=True)

    class Meta:
        table_name = "reviews"


class Email_message(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    smtpEmail = TextField(column_name="smtp_email", null=True)
    recipient = TextField(column_name="recipient", null=True)
    subject = TextField(column_name="subject", null=True)
    body = TextField(column_name="body", null=True)
    date = DateTimeField(column_name="date", null=True)

    class Meta:
        table_name = "email_messages"


class Notification(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    recipient_id = IntegerField(column_name="recipient_id", null=True)
    recipient_email = TextField(column_name="recipient_email", null=True)
    subject = TextField(column_name="subject", null=True)
    body = TextField(column_name="body", null=True)
    date = DateTimeField(column_name="date", null=True)

    class Meta:
        table_name = "notifications"


class Error(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    error = TextField(column_name="error", null=True)
    description = TextField(column_name="description", null=True)
    source = TextField(column_name="source", null=True)
    date = DateTimeField(column_name="date", null=True)

    class Meta:
        table_name = "errors"


class Exchange_rate(BaseModel):
    id = PrimaryKeyField(column_name="id", primary_key=True, unique=True)
    currency = TextField(column_name="currency", null=True)
    value = IntegerField(column_name="value", null=True)

    class Meta:
        table_name = "exchange_rate"
