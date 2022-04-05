from database import db, User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_post, Tag
from datetime import datetime
from functions import data_ordering

now = datetime.now()
tables = [User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_post, Tag]

db.drop_tables(tables)
db.create_tables(tables)

Tag.insert_many(data_ordering.tags).execute()

print("success")
