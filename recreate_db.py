from database import db, User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, \
    Tag, Review, Post_product
from datetime import datetime

now = datetime.now()
# tables = [User, Order, Post, Shop, Error, Email_message, Users_addresses, Package, Tag_of_shops, Tag]
tables = []

db.drop_tables(tables)
db.create_tables(tables)


admin = User.select().where(User.email == "octoglobal@2083492octoglobal")
if admin.exists():
    admin = admin.get()
    admin.verifiedEmail = True
    admin.statusId = 9
    admin.save()

admin = User.select().where(User.email == "octoglobal@octoglobal.ru")
if admin.exists():
    admin = admin.get()
    admin.verifiedEmail = True
    admin.statusId = 9
    admin.save()

# tags = [
#     {'id': 1, 'title': 'DJ'},
#     {'id': 2, 'title': 'Автозапчасти'},
#     {'id': 3, 'title': 'Автоматика'},
#     {'id': 4, 'title': 'Автошины'},
#     {'id': 5, 'title': 'Аккумуляторы'},
#     {'id': 6, 'title': 'Аксессуары'},
#     {'id': 7, 'title': 'Активный образ жизни'},
#     {'id': 8, 'title': 'Аптека'},
#     {'id': 9, 'title': 'Аудио'},
#     {'id': 10, 'title': 'Аудио и HiFi'},
#     {'id': 11, 'title': 'БАД'},
#     {'id': 12, 'title': 'Бег'},
#     {'id': 13, 'title': 'Био и Веган'},
#     {'id': 14, 'title': 'Бытовая техника'},
#     {'id': 15, 'title': 'Вело'},
#     {'id': 16, 'title': 'Велотовары'},
#     {'id': 17, 'title': 'Винтаж'},
#     {'id': 18, 'title': 'Витамины'},
#     {'id': 19, 'title': 'Витамины и БАДы'},
#     {'id': 20, 'title': 'Все для дома и интерьера'},
#     {'id': 21, 'title': 'Все для офиса'},
#     {'id': 22, 'title': 'Гаражные ворота и аксессуары'},
#     {'id': 23, 'title': 'Гольф'},
#     {'id': 24, 'title': 'Гопро'},
#     {'id': 25, 'title': 'Дайвинг'},
#     {'id': 26, 'title': 'Детские автокресла'},
#     {'id': 27, 'title': 'Детские товары'},
#     {'id': 28, 'title': 'Детский сад'},
#     {'id': 29, 'title': 'Джип'},
#     {'id': 30, 'title': 'Для геймеров'},
#     {'id': 31, 'title': 'Для диабетиков'},
#     {'id': 32, 'title': 'Для ухода за бородой'},
#     {'id': 33, 'title': 'Для школ и универа'},
#     {'id': 34, 'title': 'Доступная среда'},
#     {'id': 35, 'title': 'Зимние виды спорта'},
#     {'id': 36, 'title': 'Идеи подарков'},
#     {'id': 37, 'title': 'Инструмент для дома'},
#     {'id': 38, 'title': 'Карнавальные костюмы'},
#     {'id': 39, 'title': 'Коллекционерам'},
#     {'id': 40, 'title': 'Компьютерная техника'},
#     {'id': 41, 'title': 'Компьютеры'},
#     {'id': 42, 'title': 'Контактные линзы'},
#     {'id': 43, 'title': 'Корейская косметика'},
#     {'id': 44, 'title': 'Косметика'},
#     {'id': 45, 'title': 'Кофе'},
#     {'id': 46, 'title': 'Кухня и сервировка'},
#     {'id': 47, 'title': 'Лед лампы'},
#     {'id': 48, 'title': 'Магнитолы'},
#     {'id': 49, 'title': 'Майнинг'},
#     {'id': 50, 'title': 'Медицина и уход'},
#     {'id': 51, 'title': 'Мототовары'},
#     {'id': 52, 'title': 'Мототовары на русском'},
#     {'id': 53, 'title': 'Мужская одежда'},
#     {'id': 54, 'title': 'Музыкальные инструменты'},
#     {'id': 55, 'title': 'Немецкая обувь'},
#     {'id': 56, 'title': 'Нижнее белье'},
#     {'id': 57, 'title': 'Носки'},
#     {'id': 58, 'title': 'Обувь'},
#     {'id': 59, 'title': 'Одежда'},
#     {'id': 60, 'title': 'Оптика'},
#     {'id': 61, 'title': 'Освещение'},
#     {'id': 62, 'title': 'Охота'},
#     {'id': 63, 'title': 'Плюс сайз'},
#     {'id': 64, 'title': 'Подводная сьемка'},
#     {'id': 65, 'title': 'Полотенца'},
#     {'id': 66, 'title': 'Премиальные бренды'},
#     {'id': 67, 'title': 'Провода'},
#     {'id': 68, 'title': 'Проекторы'},
#     {'id': 69, 'title': 'Распрадажа'},
#     {'id': 70, 'title': 'Распродажа'},
#     {'id': 71, 'title': 'Розетки'},
#     {'id': 72, 'title': 'Рыбалка'},
#     {'id': 73, 'title': 'Рюкзаки'},
#     {'id': 74, 'title': 'Сад и огород'},
#     {'id': 75, 'title': 'Сантехника'},
#     {'id': 76, 'title': 'Сим рейсинг'},
#     {'id': 77, 'title': 'Симуляторы'},
#     {'id': 78, 'title': 'Скейт и серф'},
#     {'id': 79, 'title': 'Слуховые аппараты'},
#     {'id': 80, 'title': 'Солнечная энергия'},
#     {'id': 81, 'title': 'Специи'},
#     {'id': 82, 'title': 'Спортивная одежда'},
#     {'id': 83, 'title': 'Спортивное питание'},
#     {'id': 84, 'title': 'Спортивные товары'},
#     {'id': 85, 'title': 'Стиль'},
#     {'id': 86, 'title': 'Студийное освещение'},
#     {'id': 87, 'title': 'Сумки'},
#     {'id': 88, 'title': 'Текстиль'},
#     {'id': 89, 'title': 'Теннис'},
#     {'id': 90, 'title': 'Товары для альпинизма'},
#     {'id': 91, 'title': 'Товары для дома и интерьера'},
#     {'id': 92, 'title': 'Товары для животных'},
#     {'id': 93, 'title': 'Товары для трекинга'},
#     {'id': 94, 'title': 'Тюнинг'},
#     {'id': 95, 'title': 'Украшения'},
#     {'id': 96, 'title': 'Украшения и часы'},
#     {'id': 97, 'title': 'Универсальные магазины'},
#     {'id': 98, 'title': 'Флористика'},
#     {'id': 99, 'title': 'Фото'},
#     {'id': 100, 'title': 'Футбол'},
#     {'id': 101, 'title': 'Хобби'},
#     {'id': 102, 'title': 'Хоккей'},
#     {'id': 103, 'title': 'Чемоданы'},
#     {'id': 104, 'title': 'Чиптюнинг'},
#     {'id': 105, 'title': 'Шитье'},
#     {'id': 106, 'title': 'Штативы'},
#     {'id': 107, 'title': 'Электроника'}
# ]
# Tag.insert_many(tags).execute()

print("success")
