from database import db, User, Order, News, Shop

tables = [User, Order, News, Shop]

db.drop_tables(tables)
db.create_tables(tables)
