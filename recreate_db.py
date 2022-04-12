from database import db, User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, \
    Tag, Review, Post_photo
from datetime import datetime

now = datetime.now()
# tables = [User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, Tag]
tables = [Post, Post_photo]

db.drop_tables(tables)
db.create_tables(tables)


admin = User.select().where(User.email == "octoglobal@2083492octoglobal")
if admin.exists():
    admin = admin.get()
    admin.verifiedEmail = True
    admin.statusId = 9
    admin.save()

# tags = [
#     {'id': 1, 'title': 'Автозапчасти'},
#     {'id': 2, 'title': 'Аксессуары'},
#     {'id': 3, 'title': 'Активный образ жизни'},
#     {'id': 4, 'title': 'Аптека'},
#     {'id': 5, 'title': 'Бег'},
#     {'id': 6, 'title': 'Бытовая техника'},
#     {'id': 7, 'title': 'Вело'},
#     {'id': 8, 'title': 'Винтаж'},
#     {'id': 9, 'title': 'Витамины и БАДы'},
#     {'id': 10, 'title': 'Все для дома и интерьера'},
#     {'id': 11, 'title': 'Гольф'},
#     {'id': 12, 'title': 'Дайвинг'},
#     {'id': 13, 'title': 'Детские автокресла'},
#     {'id': 14, 'title': 'Детские товары'},
#     {'id': 15, 'title': 'Детский сад'},
#     {'id': 16, 'title': 'Для ухода за бородой'},
#     {'id': 17, 'title': 'Зимние виды спорта'},
#     {'id': 18, 'title': 'Идеи подарков'},
#     {'id': 19, 'title': 'Инструменты для дома'},
#     {'id': 20, 'title': 'Карнавальные костюмы'},
#     {'id': 21, 'title': 'Коллекционерам'},
#     {'id': 22, 'title': 'Компьютерная техника'},
#     {'id': 23, 'title': 'Контактные линзы и очки'},
#     {'id': 24, 'title': 'Корейская косметика'},
#     {'id': 25, 'title': 'Косметика'},
#     {'id': 26, 'title': 'Кофе'},
#     {'id': 27, 'title': 'Мужская одежда'},
#     {'id': 28, 'title': 'Немецкая обувь'},
#     {'id': 29, 'title': 'Нижнее белье'},
#     {'id': 30, 'title': 'Носки'},
#     {'id': 31, 'title': 'Обувь'},
#     {'id': 32, 'title': 'Одежда'},
#     {'id': 33, 'title': 'Оптика'},
#     {'id': 34, 'title': 'Освещение'},
#     {'id': 35, 'title': 'Плюс сайз'},
#     {'id': 36, 'title': 'Полотенца'},
#     {'id': 37, 'title': 'Премиальные бренды'},
#     {'id': 38, 'title': 'Распродажа'},
#     {'id': 39, 'title': 'Рюкзаки'},
#     {'id': 40, 'title': 'Сад и огород'},
#     {'id': 41, 'title': 'Сантехника'},
#     {'id': 42, 'title': 'Семена'},
#     {'id': 43, 'title': 'Скейт и серф'},
#     {'id': 44, 'title': 'Спортивная одежда'},
#     {'id': 45, 'title': 'Спортивное питание'},
#     {'id': 46, 'title': 'Спортивные товары'},
#     {'id': 47, 'title': 'Сумки'},
#     {'id': 48, 'title': 'Текстиль'},
#     {'id': 49, 'title': 'Теннис'},
#     {'id': 50, 'title': 'Товары для альпинизма'},
#     {'id': 51, 'title': 'Товары для дома и интерьера'},
#     {'id': 52, 'title': 'Товары для животных'},
#     {'id': 53, 'title': 'Товары для трекинга'},
#     {'id': 54, 'title': 'Украшения'},
#     {'id': 55, 'title': 'Украшения и часы'},
#     {'id': 56, 'title': 'Универсальные магазины'},
#     {'id': 57, 'title': 'Флористика'},
#     {'id': 58, 'title': 'Футбол'},
#     {'id': 59, 'title': 'Хобби'},
#     {'id': 60, 'title': 'Хоккей'},
#     {'id': 61, 'title': 'Чемоданы'},
#     {'id': 62, 'title': 'Шитье'},
#     {'id': 63, 'title': 'Электроника'}
# ]
# Tag.insert_many(tags).execute()

print("success")
