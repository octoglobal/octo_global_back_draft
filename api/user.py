from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from playhouse.shortcuts import model_to_dict
from peewee import fn
from datetime import datetime
import math
import itertools
from database import User, Users_addresses, Order, Shop, Tag, Tag_of_shops, Review, Post, Post_photo
from functions import data_ordering

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
        Users_addresses.create(
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
        return jsonify({"message": "success"}), 200

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


@user_api.route("/user/orders", methods=["GET", "POST", "DELETE"])
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
            .where(Order.userId == user_id)\
            .order_by(Order.id.desc()).dicts()
        for order in list(user_orders):
            order["tracking_link"] = "https://gdeposylka.ru/" + str(order["trackNumber"])
        return jsonify({"orders": list(user_orders)}), 200

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

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            order_id = str(request_data["orderId"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        order = Order.select().where(Order.id == order_id, Order.userId == user_id, Order.statusId == 0)
        if not order.exists():
            return "order not found or has an invalid status", 403
        order.get().delete_instance()
        return jsonify({"message": "success"}), 200


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
        return jsonify({"shops": shops_list}), 200


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
        page_limit = 6
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
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
        page_limit = 10
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                page = 1
        except Exception:
            page = 1
        offset = (page - 1) * page_limit
        posts = Post.select().offset(offset).limit(page_limit).order_by(Post.id.desc())
        post_photos = Post_photo.select(Post_photo.id, Post_photo.post_id, Post_photo.image_hash)\
            .where(Post_photo.post_id << posts).order_by(Post_photo.id)
        for post in posts:
            post_photo_list = []
            for post_photo in post_photos:
                if post.id == post_photo.post_id:
                    post_photo_list.append({"photo_id": post_photo.id, "photo_hash": post_photo.image_hash})
            post_dict = model_to_dict(post)
            del post_dict["statusId"]
            post_dict["photos"] = post_photo_list
            posts_list.append(post_dict)
        answer = {"posts": posts_list}
        if page == 1:
            posts_count = int(Post.select(fn.count(Post.id)).get().count)
            pages_count = math.ceil(posts_count / page_limit)
            if pages_count == 0:
                pages_count = 1
            answer["pages_count"] = pages_count
        return jsonify(answer), 200
