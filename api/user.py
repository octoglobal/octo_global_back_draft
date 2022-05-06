from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from playhouse.shortcuts import model_to_dict
from peewee import fn
from datetime import datetime
import math
import itertools
from database import User, Users_addresses, Order, Shop, Tag, Tag_of_shops, Review, Post, Post_product, Package
from functions import data_ordering, email_sending
import config

user_api = Blueprint("user_api", __name__)


@user_api.route("/egg", methods=["GET"])
def egg():
    if request.method == "GET":
        return "Oh, Hi Mark", 200


@user_api.route("/user", methods=["GET", "PATCH"])
@jwt_required()
def user_data():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address_string,
                                                Users_addresses.phone, Users_addresses.name, Users_addresses.surname,
                                                Users_addresses.longitude, Users_addresses.latitude) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True)\
            .order_by(Users_addresses.id).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data}), 200

    if request.method == "PATCH":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        request_data = request.get_json()
        for patch_key in ["name", "surname", "phone"]:
            try:
                patch_data = str(request_data[patch_key])
                if patch_key == "name":
                    user.name = patch_data
                elif patch_key == "surname":
                    user.surname = patch_data
                elif patch_key == "phone":
                    user.phone = patch_data
            except Exception:
                pass
        user.save()
        return jsonify({"message": "success"}), 200


@user_api.route("/user/address", methods=["POST", "DELETE"])
@jwt_required()
def address_info():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            name = str(request_data["name"])
            surname = str(request_data["surname"])
            address_string = str(request_data["address_string"])
            latitude = str(request_data["latitude"])
            longitude = str(request_data["longitude"])
            phone = str(request_data["phone"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        new_address = Users_addresses.create(
            userId=user_id,
            name=name,
            surname=surname,
            address_string=address_string,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            delete=False,
            createdTime=datetime.now()
        )
        return jsonify({"message": "success", "addressId": new_address.id}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            address_id = str(request_data["address_id"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        address = Users_addresses.select() \
            .where(Users_addresses.id == address_id,
                   Users_addresses.userId == user_id,
                   Users_addresses.address_string != True)
        if not address.exists():
            return "address not found", 403
        address = address.get()
        address.deletedTime = datetime.now()
        address.delete = True
        address.save()
        return jsonify({"message": "success"}), 200


@user_api.route("/user/orders", methods=["GET", "POST"])
@jwt_required()
def orders_info():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user_orders = Order.select(Order.id, Order.longId, Order.userId, Order.title, Order.comment, Order.trackNumber,
                                   Order.statusId, Order.createdTime) \
            .where(Order.userId == user_id, ((Order.statusId == 0) | (Order.statusId == 1)))\
            .order_by(Order.id.desc()).dicts()
        for order in list(user_orders):
            order["tracking_link"] = "https://gdeposylka.ru/" + str(order["trackNumber"])
        user_packages = list(Package
                             .select(Package.id, Package.longId, Package.addressId,
                                     Package.statusId, Package.trackNumber)
                             .where(Order.userId == user_id)
                             .join(Order, on=(Package.id == Order.packageId))
                             .group_by(Package).dicts())
        user_packages_orders = list(Order.select(Order.id, Order.longId, Order.userId, Order.title, Order.comment,
                                                 Order.trackNumber, Order.statusId, Order.createdTime, Order.packageId)
                                    .where(Order.userId == user_id).join(Package, on=(Order.packageId == Package.id))
                                    .dicts())
        user_packages_addresses_ids = [temp["addressId"] for temp in user_packages]
        if None in user_packages_addresses_ids:
            user_packages_addresses_ids.remove(None)
        user_packages_addresses = list(Users_addresses
                                       .select(Users_addresses.id, Users_addresses.address_string,
                                               Users_addresses.phone, Users_addresses.name, Users_addresses.surname,
                                               Users_addresses.longitude, Users_addresses.latitude)
                                       .where(Users_addresses.userId == user_id, Users_addresses.delete != True,
                                              Users_addresses.id << user_packages_addresses_ids).dicts())
        for user_package in user_packages:
            if user_package["addressId"]:
                package_address = next(i for i in user_packages_addresses if i["id"] == user_package["addressId"])
                user_package["address"] = package_address
            else:
                user_package["address"] = None
            if user_package["trackNumber"]:
                user_package["tracking_link"] = "https://gdeposylka.ru/" + str(user_package["trackNumber"])
            else:
                user_package["tracking_link"] = None
            user_packages_orders_list = []
            for user_packages_order in user_packages_orders:
                if user_packages_order["packageId"] == user_package["id"]:
                    user_packages_orders_list.append(user_packages_order)
            user_package["orders"] = user_packages_orders_list
        return jsonify({"orders": list(user_orders), "packages": user_packages}), 200

    if request.method == "POST":
        request_data = request.get_json()
        try:
            track_number = str(request_data["track_number"])
            title = str(request_data["title"])
            comment = str(request_data["comment"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        if Order.get_or_none(userId=user_id, trackNumber=track_number) is not None:
            return "order with this track number already exists", 409
        long_id = data_ordering.make_order_long_id()
        Order.create(
            userId=user_id,
            longId=long_id,
            title=title,
            comment=comment,
            statusId=0,
            trackNumber=track_number,
            createdTime=datetime.now()
        )
        return jsonify({"message": "success"}), 200

    # if request.method == "DELETE":
    #     request_data = request.get_json()
    #     try:
    #         order_id = str(request_data["orderId"])
    #     except Exception:
    #         return "invalid data", 422
    #     token_data = get_jwt_identity()
    #     user_id = token_data["user_id"]
    #     user = User.select().where(User.id == user_id)
    #     if not user.exists():
    #         return "user not found", 403
    #     order = Order.select().where(Order.id == order_id, Order.userId == user_id, Order.statusId == 0)
    #     if not order.exists():
    #         return "order not found or has an invalid status", 403
    #     order.get().delete_instance()
    #     return jsonify({"message": "success"}), 200


@user_api.route("/user/orders/expected", methods=["GET"])
@jwt_required()
def orders_expected_info():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                page_limit = 6
        except Exception:
            page_limit = 10
        offset = (page - 1) * page_limit
        user_orders = Order.select(Order.id, Order.longId, Order.userId, Order.title, Order.comment, Order.trackNumber,
                                   Order.statusId, Order.createdTime) \
            .where(Order.userId == user_id, Order.statusId == 0)\
            .order_by(Order.id.desc()).offset(offset).limit(page_limit).dicts()
        for order in list(user_orders):
            order["tracking_link"] = "https://gdeposylka.ru/" + str(order["trackNumber"])
        return jsonify({"orders": list(user_orders)}), 200


@user_api.route("/user/orders/are_waiting", methods=["GET"])
@jwt_required()
def orders_are_waiting_info():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                page_limit = 6
        except Exception:
            page_limit = 10
        offset = (page - 1) * page_limit
        try:
            package_pages = args["package"][0]
            if package_pages == "true":
                try:
                    user_packages = list(Package
                                         .select(Package.id, Package.longId, Package.addressId,
                                                 Package.statusId, Package.trackNumber)
                                         .where(Order.userId == user_id, ((Package.statusId == 0) |
                                                                          (Package.statusId == 1) |
                                                                          (Package.statusId == 2) |
                                                                          (Package.statusId == 4)))
                                         .join(Order, on=(Package.id == Order.packageId))
                                         .order_by(Package.id.desc()).offset(offset).limit(page_limit)
                                         .group_by(Package).dicts())
                    user_packages_orders = list(Order.select(Order.id, Order.longId, Order.userId, Order.title,
                                                             Order.comment, Order.trackNumber, Order.statusId,
                                                             Order.createdTime, Order.packageId)
                                                .where(Order.userId == user_id)
                                                .join(Package, on=(Order.packageId == Package.id))
                                                .order_by(Order.id.desc()).dicts())
                    user_packages_addresses_ids = [temp["addressId"] for temp in user_packages]
                    if None in user_packages_addresses_ids:
                        user_packages_addresses_ids.remove(None)
                    user_packages_addresses = list(Users_addresses
                                                   .select(Users_addresses.id, Users_addresses.address_string,
                                                           Users_addresses.phone, Users_addresses.name,
                                                           Users_addresses.surname, Users_addresses.longitude,
                                                           Users_addresses.latitude)
                                                   .where(Users_addresses.userId == user_id,
                                                          Users_addresses.delete != True,
                                                          Users_addresses.id << user_packages_addresses_ids).dicts())
                    for user_package in user_packages:
                        if user_package["addressId"]:
                            package_address = next(i for i in user_packages_addresses
                                                   if i["id"] == user_package["addressId"])
                            user_package["address"] = package_address
                        else:
                            user_package["address"] = None
                        if user_package["trackNumber"]:
                            user_package["tracking_link"] = "https://gdeposylka.ru/" + str(user_package["trackNumber"])
                        else:
                            user_package["tracking_link"] = None
                        user_packages_orders_list = []
                        for user_packages_order in user_packages_orders:
                            if user_packages_order["packageId"] == user_package["id"]:
                                user_packages_orders_list.append(user_packages_order)
                        user_package["orders"] = user_packages_orders_list
                    return jsonify({"packages": user_packages}), 200
                except Exception:
                    return "packages loading error", 500
        except Exception:
            pass
        user_orders = Order.select(Order.id, Order.longId, Order.userId, Order.title, Order.comment, Order.trackNumber,
                                   Order.statusId, Order.createdTime) \
            .where(Order.userId == user_id, Order.statusId == 1)\
            .order_by(Order.id.desc()).offset(offset).limit(page_limit).dicts()
        for order in list(user_orders):
            order["tracking_link"] = "https://gdeposylka.ru/" + str(order["trackNumber"])
        return jsonify({"orders": list(user_orders)}), 200


@user_api.route("/user/orders/sent", methods=["GET"])
@jwt_required()
def orders_sent_info():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                page_limit = 6
        except Exception:
            page_limit = 10
        offset = (page - 1) * page_limit
        try:
            user_packages = list(Package
                                 .select(Package.id, Package.longId, Package.addressId,
                                         Package.statusId, Package.trackNumber)
                                 .where(Order.userId == user_id, Package.statusId == 3)
                                 .join(Order, on=(Package.id == Order.packageId))
                                 .order_by(Package.id.desc()).offset(offset).limit(page_limit)
                                 .group_by(Package).dicts())
            user_packages_orders = list(Order.select(Order.id, Order.longId, Order.userId, Order.title,
                                                     Order.comment, Order.trackNumber, Order.statusId,
                                                     Order.createdTime, Order.packageId)
                                        .where(Order.userId == user_id)
                                        .join(Package, on=(Order.packageId == Package.id))
                                        .order_by(Order.id.desc()).dicts())
            user_packages_addresses_ids = [temp["addressId"] for temp in user_packages]
            if None in user_packages_addresses_ids:
                user_packages_addresses_ids.remove(None)
            user_packages_addresses = list(Users_addresses
                                           .select(Users_addresses.id, Users_addresses.address_string,
                                                   Users_addresses.phone, Users_addresses.name,
                                                   Users_addresses.surname, Users_addresses.longitude,
                                                   Users_addresses.latitude)
                                           .where(Users_addresses.userId == user_id,
                                                  Users_addresses.delete != True,
                                                  Users_addresses.id << user_packages_addresses_ids).dicts())
            for user_package in user_packages:
                if user_package["addressId"]:
                    package_address = next(i for i in user_packages_addresses
                                           if i["id"] == user_package["addressId"])
                    user_package["address"] = package_address
                else:
                    user_package["address"] = None
                if user_package["trackNumber"]:
                    user_package["tracking_link"] = "https://gdeposylka.ru/" + str(user_package["trackNumber"])
                else:
                    user_package["tracking_link"] = None
                user_packages_orders_list = []
                for user_packages_order in user_packages_orders:
                    if user_packages_order["packageId"] == user_package["id"]:
                        user_packages_orders_list.append(user_packages_order)
                user_package["orders"] = user_packages_orders_list
            return jsonify({"packages": user_packages}), 200
        except Exception as e:
            print(e)
            return "packages loading error", 500


@user_api.route("/shops", methods=["GET"])
def shop_info():
    if request.method == "GET":
        shops_list = []
        page_limit = 12
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            tags = []
            for tag in args["tag"]:
                try:
                    tags.append(int(tag))
                except Exception:
                    pass
            db_tags = Tag.select().where(Tag.id << tags)
        except Exception:
            db_tags = []
        try:
            search_string = str(args["search_suggestions"][0])
            search_results_limit = 3
            search_shops_startswith = Shop.select(Shop.title, Shop.url)\
                .where(Shop.title.startswith(search_string)).limit(search_results_limit).order_by(Shop.title)
            search_shops_contains = Shop.select(Shop.title, Shop.url)\
                .where(Shop.title.contains(search_string), ~(Shop.title.startswith(search_string)))\
                .limit(search_results_limit - len(search_shops_startswith)).order_by(Shop.title)
            search_results = list(search_shops_startswith.dicts()) + list(search_shops_contains.dicts())
            return jsonify({"search_suggestions_results": search_results}), 200
        except Exception:
            pass
        try:
            search_results = []
            search_string = str(args["search"][0])
            search_results_limit = 12
            search_shops_startswith = Shop.select()\
                .where(Shop.title.startswith(search_string)).limit(search_results_limit).order_by(Shop.title)
            search_shops_contains = Shop.select()\
                .where(Shop.title.contains(search_string), ~(Shop.title.startswith(search_string)))\
                .limit(search_results_limit - len(search_shops_startswith)).order_by(Shop.title)
            shops_tags = Tag_of_shops.select(Tag_of_shops.shop_id, Tag_of_shops.tag_id, Tag.title)\
                .where(Tag_of_shops.shop_id << search_shops_startswith | Tag_of_shops.shop_id << search_shops_contains)\
                .join(Tag, on=(Tag_of_shops.tag_id == Tag.id))
            for shop in itertools.chain(search_shops_startswith, search_shops_contains):
                shop_tags_list = []
                for shop_tag in shops_tags:
                    if shop.id == shop_tag.shop_id:
                        shop_tags_list.append({"shop_tag_id": shop_tag.tag_id, "shop_tag_title": shop_tag.tag.title})
                shop_dict = model_to_dict(shop)
                shop_dict["tags"] = shop_tags_list
                search_results.append(shop_dict)
            return jsonify({"search_results": search_results}), 200
        except Exception:
            pass
        offset = (page - 1) * page_limit
        if len(db_tags) > 0:
            shops = Shop.select().offset(offset).limit(page_limit).where(Tag_of_shops.tag_id << db_tags)\
                .join(Tag_of_shops, on=(Shop.id == Tag_of_shops.shop_id)).order_by(Shop.title).group_by(Shop.id)
        else:
            shops = Shop.select().offset(offset).limit(page_limit).order_by(Shop.title)
        shops_tags = Tag_of_shops.select(Tag_of_shops.shop_id, Tag_of_shops.tag_id, Tag.title)\
            .where(Tag_of_shops.shop_id << shops).join(Tag, on=(Tag_of_shops.tag_id == Tag.id))
        for shop in shops:
            shop_tags_list = []
            for shop_tag in shops_tags:
                if shop.id == shop_tag.shop_id:
                    shop_tags_list.append({"shop_tag_id": shop_tag.tag_id, "shop_tag_title": shop_tag.tag.title})
            shop_dict = model_to_dict(shop)
            shop_dict["tags"] = shop_tags_list
            shops_list.append(shop_dict)
        return jsonify({"shops": shops_list, "postsOnPage": page_limit}), 200


@user_api.route("/shops_tags", methods=["GET", "PATCH"])
def shops_tags_info():
    if request.method == "GET":
        shops_tags = list(Tag.select().dicts())
        return jsonify({"shops_tags": shops_tags}), 200


@user_api.route("/add_review", methods=["POST"])
@jwt_required()
def add_reviews():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            text = str(request_data["text"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        Review.create(
            user_id=user_id,
            text=text,
            createdTime=datetime.now()
        )
        return jsonify({"message": "success"}), 200


@user_api.route("/reviews", methods=["GET"])
def reviews_info():
    if request.method == "GET":
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                page_limit = 6
        except Exception:
            page_limit = 6
        offset = (page - 1) * page_limit
        reviews = list(Review
                       .select(Review.id, Review.text, Review.createdTime, User.name.alias("userName"))
                       .join(User, on=(Review.user_id == User.id))
                       .order_by(Review.id.desc()).dicts().offset(offset).limit(page_limit))
        answer = {"reviews": reviews}
        if page == 1:
            reviews_count = int(Review.select(fn.count(Review.id)).get().count)
            pages_count = math.ceil(reviews_count/page_limit)
            if pages_count == 0:
                pages_count = 1
            answer["pages_count"] = pages_count
        return jsonify(answer), 200


@user_api.route("/blog", methods=["GET"])
def blog_info():
    if request.method == "GET":
        posts_list = []
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                page_limit = 10
        except Exception:
            page_limit = 10
        offset = (page - 1) * page_limit
        posts = Post.select().offset(offset).limit(page_limit).order_by(Post.id.desc())
        post_products = Post_product\
            .select(Post_product.id, Post_product.postId, Post_product.title, Post_product.body,
                    Post_product.photo, Post_product.url)\
            .where(Post_product.postId << posts).order_by(Post_product.id)
        for post in posts:
            post_products_list = []
            for post_product in post_products:
                if post.id == post_product.postId:
                    post_products_list.append({
                        "title": post_product.title,
                        "body": post_product.body,
                        "photo": post_product.photo,
                        "url": post_product.url
                    })
            post_dict = model_to_dict(post)
            del post_dict["statusId"]
            post_dict["products"] = post_products_list
            posts_list.append(post_dict)
        answer = {"posts": posts_list}
        if page == 1:
            posts_count = int(Post.select(fn.count(Post.id)).get().count)
            pages_count = math.ceil(posts_count / page_limit)
            if pages_count == 0:
                pages_count = 1
            answer["pages_count"] = pages_count
        return jsonify(answer), 200


@user_api.route("/user/package", methods=["POST", "DELETE"])
@jwt_required()
def user_packages_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            request_orders = request_data["orders"]
            if type(request_orders) != list:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user_orders = Order.select().where(Order.userId == user_id, Order.statusId == 1, Order.id << request_orders)
        if len(list(user_orders.dicts())) != len(request_orders):
            return jsonify({"error": "Не все посылки из списка готовы к объединению"}), 460
        long_id = data_ordering.make_package_long_id()
        package = Package.create(
            longId=long_id,
            userId=user_id,
            statusId=0,
            createdTime=datetime.now()
        )
        package_id = package.id
        package_dict = model_to_dict(package)
        query = Order.update(statusId=2, packageId=package_id)\
            .where(Order.userId == user_id, Order.statusId == 1, Order.id << request_orders)
        query.execute()
        return jsonify({"message": "success", "package": package_dict}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            package_id = request_data["packageId"]
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        package = Package.select() \
            .where(Package.id == package_id, Package.userId == user_id, Package.statusId == 0)
        if not package.exists():
            return "package not found", 403
        user_orders = Order.select() \
            .where(Order.userId == user_id,
                   Order.statusId == 2,
                   Order.packageId == package_id,
                   Package.id == package_id,
                   Package.userId == user_id,
                   ((Package.statusId == 0) | (Package.statusId == 1) | (Package.statusId == 2))) \
            .join(Package, on=(Order.packageId == Package.id))
        Order.update(statusId=1, packageId=None).where(Order.id << user_orders).execute()
        package.get().delete_instance()
        return jsonify({"message": "success"}), 200


@user_api.route("/user/package/address", methods=["POST"])
@jwt_required()
def user_packages_address_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            package_id = request_data["packageId"]
            address_id = request_data["addressId"]
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user_address = Users_addresses.select()\
            .where(Users_addresses.userId == user_id, Users_addresses.id == address_id)
        if not user_address.exists():
            return "address not found", 403
        package = Package.select().where(Package.id == package_id, Package.userId == user_id,
                                         ((Package.statusId == 0) | (Package.statusId == 1)))
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.addressId = address_id
        package.statusId = 2
        package.save()
        user_dict = model_to_dict(user.get())
        package_dict = model_to_dict(package)
        address_dict = model_to_dict(user_address.get())
        if not email_sending.send_registration_of_the_parcel(config.admin_delivery_info_email,
                                                             "Octo Global: Оповещение", user_dict,
                                                             package_dict, address_dict):
            return jsonify({"message": "success", "sendEmail": False}), 201
        return jsonify({"message": "success", "sendEmail": True}), 200

    # if request.method == "DELETE":
    #     request_data = request.get_json()
    #     try:
    #         package_id = request_data["packageId"]
    #     except Exception:
    #         return "invalid data", 422
    #     token_data = get_jwt_identity()
    #     user_id = token_data["user_id"]
    #     user = User.select().where(User.id == user_id)
    #     if not user.exists():
    #         return "user not found", 403
    #     package = Package.select().where(Package.id == package_id)
    #     if not package.exists():
    #         return "package not found", 403
    #     user_orders = Order.select() \
    #         .where(Order.userId == user_id, Order.statusId == 2,
    #         Order.packageId == package_id, Package.statusId == 0) \
    #         .join(Package, on=(Order.packageId == Package.id))
    #     Order.update(statusId=1, packageId=None).where(Order.id << user_orders).execute()
    #     package.get().delete_instance()
    #     return jsonify({"message": "success"}), 200


@user_api.route("/user/send_message/<order_action>/<order_id>", methods=["GET"])
@jwt_required()
def send_email_messages(order_action, order_id):

    if request.method == "GET":
        if order_action not in ["order_return", "order_check"]:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        order = Order.select().where(Order.id == order_id, Order.userId == user_id)
        if not order.exists():
            return "order not found or has an invalid status", 403
        user_dict = model_to_dict(user.get())
        order_dict = model_to_dict(order.get())
        if order_action == "order_return":
            if not email_sending.send_order_return(config.admin_delivery_info_email, "Octo Global: Оповещение",
                                                   user_dict, order_dict):
                return "email send error", 500

        if order_action == "order_check":
            if not email_sending.send_order_check(config.admin_delivery_info_email, "Octo Global: Оповещение",
                                                  user_dict, order_dict):
                return "email send error", 500
        return jsonify({"message": "success"}), 200
