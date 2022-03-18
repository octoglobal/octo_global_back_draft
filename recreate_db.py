from database import db, User, Order, News, Shop, Error, Email_message
from datetime import datetime

now = datetime.now()
tables = [User, Order, News, Shop, Error, Email_message]

db.drop_tables(tables)
db.create_tables(tables)

User.create(email="email", name="name", surname="surname", verifiedEmail=False, registrationTime=now, statusId=0)
User.create(email="email1", name="name", surname="surname", verifiedEmail=False, registrationTime=now, statusId=0)
User.create(email="email2", name="name", surname="surname", verifiedEmail=False, registrationTime=now, statusId=0)

artist = User.select().where(User.email == "email2").get()
artist.name = "updated_name"
artist.save()

user_obj = User.select().where(User.email == 'email2').dicts().get()
print(user_obj)
