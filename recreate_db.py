from database import db, User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, Tag
from datetime import datetime

now = datetime.now()
tables = [User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, Tag]

db.drop_tables(tables)
db.create_tables(tables)

tags = [
    {
        "id": 1,
        "title": "Одежда"
    },
    {
        "id": 2,
        "title": "Электроника"
    },
    {
        "id": 3,
        "title": "Туризм"
    },
    {
        "id": 4,
        "title": "Сувениры"
    }
]

Tag.insert_many(tags).execute()

print("success")
