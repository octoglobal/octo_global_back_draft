from database import db, User, Order, News, Shop, Error, Email_message, Users_addresses
from datetime import datetime

now = datetime.now()
tables = [User, Order, News, Shop, Error, Email_message, Users_addresses]

db.drop_tables(tables)
db.create_tables(tables)

print("success")
