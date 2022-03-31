from database import db, User, Order, News, Shop, Error, Email_message, Users_addresses, Package
from datetime import datetime

now = datetime.now()
tables = [User, Order, News, Shop, Error, Email_message, Users_addresses, Package]

db.drop_tables(tables)
db.create_tables(tables)

print("success")
