from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import json
from datetime import datetime
from database import Shop, Tag_of_shops, Tag, Review, Post, Post_photo, User, Order, Package
from functions import images_func, data_ordering

admin_api = Blueprint("admin_api", __name__)


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # token_data = get_jwt_identity()
        # try:
        #     admin_token_check = token_data["status"]
        # except Exception:
        #     return "rights error", 406
        # if admin_token_check != 9:
        #     return "rights error", 406
        return func(*args, **kwargs)

    return decorated_function


@admin_api.route("/admin/shop", methods=["POST"])
@jwt_required()
@admin_required
def admin_shop_actions():
    if request.method == "POST":
        request_files = request.files.to_dict(flat=False)
        request_form = request.form.to_dict(flat=False)
        try:
            request_data_list = request_form["json_data"]
            if len(request_data_list) != 1:
                return "invalid data", 422
            string_request_data = request_data_list[0]
            request_data = json.loads(string_request_data)
            alias = str(request_data["alias"])
            title = str(request_data["title"])
            description = str(request_data["description"])
            price_id = int(request_data["priceId"])
            url = str(request_data["url"])
            tags = request_data["tags"]
            if type(tags) != list:
                return "invalid data", 422
            project_tags = list(Tag.select().dicts())
            project_tags = [temp["id"] for temp in project_tags]
            for tag in tags:
                if type(tag) != int or tag <= 0 or len(tags) != len(set(tags)) or tag not in project_tags:
                    return "invalid data", 422
        except Exception:
            return "invalid data", 422
        if Shop.get_or_none(alias=alias) is not None:
            return "shop with this alias already exists", 409
        try:
            image_list = request_files["image"]
            logo_list = request_files["logo"]
            if len(image_list) != 1 or len(logo_list) != 1:
                return "invalid data", 422
            image_file = image_list[0]
            logo_file = logo_list[0]
        except Exception:
            return "invalid data", 422
        try:
            photo = images_func.save_image(image_file, 1600)
            logo = images_func.save_image(logo_file, 500)
        except Exception:
            return "image loading error", 422
        try:
            shop = Shop.create(
                alias=alias,
                title=title,
                description=description,
                photo=photo,
                logo=logo,
                priceId=price_id,
                url=url
            )
            shop_id = shop.id
            tag_of_posts_data = []
            for tag in tags:
                tag_of_posts_data.append({"shop_id": shop_id, "tag_id": tag})
            Tag_of_shops.insert_many(tag_of_posts_data).execute()
        except Exception:
            return "internal server error", 500
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/review", methods=["DELETE"])
@jwt_required()
@admin_required
def admin_review_actions():
    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            review_id = int(request_data["reviewId"])
        except Exception:
            return "invalid data", 422
        review = Review.select().where(Review.id == review_id)
        if not review.exists():
            return "review not found", 403
        review.get().delete_instance()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/blog", methods=["POST", "PATCH", "DELETE"])
@jwt_required()
@admin_required
def admin_blog_actions():
    if request.method == "POST":
        request_files = request.files.to_dict(flat=False)
        request_form = request.form.to_dict(flat=False)
        try:
            request_data_list = request_form["json_data"]
            if len(request_data_list) != 1:
                return "invalid data", 422
            string_request_data = request_data_list[0]
            request_data = json.loads(string_request_data)
            title = str(request_data["title"])
            body = str(request_data["body"])
        except Exception:
            return "invalid data", 422
        try:
            images_list = request_files["image"]
            if len(images_list) > 10:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
        images = []
        try:
            for image_file in images_list:
                image = images_func.save_image(image_file, 1600)
                images.append(image)
        except Exception:
            return "image loading error", 422
        try:
            post = Post.create(
                title=title,
                body=body,
                statusId=0,
                createdTime=datetime.now()
            )
            post_id = int(post.id)
            images_of_post_data = []
            for image_hash in images:
                images_of_post_data.append({"image_hash": image_hash, "post_id": post_id, "statusId": 0})
            Post_photo.insert_many(images_of_post_data).execute()
        except Exception:
            return "internal server error", 500
        return jsonify({"message": "success"}), 200

    if request.method == "PATCH":
        request_files = request.files.to_dict(flat=False)
        request_form = request.form.to_dict(flat=False)
        try:
            request_data_list = request_form["json_data"]
            if len(request_data_list) != 1:
                return "invalid data", 422
            string_request_data = request_data_list[0]
            request_data = json.loads(string_request_data)
            post_id = int(request_data["blogId"])
            title = str(request_data["title"])
            body = str(request_data["body"])
        except Exception:
            return "invalid data", 422
        try:
            images_list = request_files["image"]
            hash_list = request_form["image"]

            print(images_list)
            print(hash_list)

            if len(images_list) > 10:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
        images = []
        try:
            for image_file in images_list:
                image = images_func.save_image(image_file, 1600)
                images.append(image)
        except Exception:
            return "image loading error", 422
        post = Post.select().where(Post.id == post_id)
        if not post.exists():
            return "blog not found", 403
        try:
            post = post.get()
            post.title = title
            post.body = body
            post.editedTime = datetime.now()
            post.save()
            Post_photo.delete().where(Post_photo.post_id == post_id).execute()
            images_of_post_data = []
            for image_hash in images:
                images_of_post_data.append({"image_hash": image_hash, "post_id": post_id, "statusId": 0})
            Post_photo.insert_many(images_of_post_data).execute()
        except Exception:
            return "internal server error", 500
        return jsonify({"message": "success"}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            blog_id = int(request_data["blogId"])
        except Exception:
            return "invalid data", 422
        blog = Post.select().where(Post.id == blog_id)
        if not blog.exists():
            return "blog not found", 403
        blog.get().delete_instance()
        Post_photo.delete().where(Post_photo.post_id == blog_id).execute()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/orders", methods=["POST", "DELETE"])
@jwt_required()
@admin_required
def admin_orders_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            track_number = str(request_data["track_number"])
            title = str(request_data["title"])
            comment = str(request_data["comment"])
            user_id = int(request_data["userId"])
        except Exception:
            return "invalid data", 422
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
            statusId=1,
            trackNumber=track_number,
            createdTime=datetime.now()
        )
        return jsonify({"message": "success"}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            order_id = str(request_data["orderId"])
            user_id = int(request_data["userId"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        order = Order.select().where(Order.id == order_id, Order.userId == user_id)
        if not order.exists():
            return "order not found or has an invalid status", 403
        order.get().delete_instance()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/packages", methods=["POST", "DELETE", "PATCH"])
@jwt_required()
@admin_required
def admin_packages_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            request_orders = request_data["orders"]
            user_id = int(request_data["userId"])
            if type(request_orders) != list:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
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
            statusId=1,
            createdTime=datetime.now(),
            agreementToConsolidationTime=datetime.now()
        )
        package_id = package.id
        query = Order.update(statusId=2, packageId=package_id) \
            .where(Order.userId == user_id, Order.statusId == 1, Order.id << request_orders)
        query.execute()
        return jsonify({"message": "success"}), 200

    if request.method == "PATCH":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            package_id = int(request_data["packageId"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 0)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 1
        package.agreementToConsolidationTime = datetime.now()
        package.save()
        return jsonify({"message": "success"}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            package_id = request_data["packageId"]
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        package = Package.select() \
            .where(Package.id == package_id,
                   Package.userId == user_id,
                   ((Package.statusId == 0) | (Package.statusId == 1)))
        if not package.exists():
            return "package not found", 403
        user_orders = Order.select() \
            .where(Order.userId == user_id,
                   Order.statusId == 2,
                   Order.packageId == package_id,
                   Package.id == package_id,
                   Package.userId == user_id,
                   ((Package.statusId == 0) | (Package.statusId == 1))) \
            .join(Package, on=(Order.packageId == Package.id))
        Order.update(statusId=1, packageId=None).where(Order.id << user_orders).execute()
        package.get().delete_instance()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/package_track", methods=["POST", "DELETE"])
@jwt_required()
@admin_required
def admin_package_track_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            track_number = str(request_data["trackNumber"])
            user_id = int(request_data["userId"])
            package_id = int(request_data["packageId"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 1)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 2
        package.trackNumber = track_number
        package.dispatchTime = datetime.now()
        package.save()
        return jsonify({"message": "success"}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            package_id = request_data["packageId"]
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 2)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 1
        package.trackNumber = None
        package.dispatchTime = None
        package.save()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/block_user", methods=["POST"])
@jwt_required()
@admin_required
def admin_user_block_actions():
    if request.method == "POST":
        request_data = request.get_json()
        token_data = get_jwt_identity()
        self_id = token_data["user_id"]
        try:
            user_id = int(request_data["userId"])
            block = request_data["block"]
            if type(block) != bool:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
        if block:
            user_status = 1
        else:
            user_status = 0
        user = User.select().where(User.id == user_id)
        if not user.exists() or user_id == self_id:
            return "user not found", 403
        user = user.get()
        user.statusId = user_status
        user.save()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/search", methods=["GET"])
@jwt_required()
@admin_required
def admin_search_actions():
    if request.method == "GET":

        # page_limit = 12
        search_results_limit = 5
        args = request.args.to_dict(flat=False)
        # try:
        #     page = int(args["page"][0])
        #     if page <= 0:
        #         page = 1
        # except Exception:
        #     page = 1

        try:
            search_string = str(args["search_suggestions"][0])
            user_long_id_search = list(User.select(User.personalAreaId, User.id)
                                       .where(User.personalAreaId.cast("TEXT").contains(search_string))
                                       .limit(search_results_limit).order_by(User.personalAreaId).dicts())
            order_long_id_search = list(Order.select(Order.longId, Order.id)
                                        .where(Order.longId.cast("TEXT").contains(search_string))
                                        .limit(search_results_limit).order_by(Order.longId).dicts())
            order_track_number_search = list(Order.select(Order.trackNumber, Order.id)
                                             .where(Order.trackNumber.contains(search_string))
                                             .limit(search_results_limit).order_by(Order.trackNumber).dicts())
            search_results = {
                "users": user_long_id_search,
                "orders_numbers": order_long_id_search,
                "orders_track_numbers": order_track_number_search
            }
            return jsonify({"search_suggestions_results": search_results}), 200
        except Exception as e:
            print(e)
            pass

        return "temp"

        # try:
        #     search_results = []
        #     search_string = str(args["search"][0])
        #     search_results_limit = 12
        #     search_shops_startswith = Shop.select() \
        #         .where(Shop.title.startswith(search_string)).limit(search_results_limit).order_by(Shop.title)
        #     search_shops_contains = Shop.select() \
        #         .where(Shop.title.contains(search_string), ~(Shop.title.startswith(search_string))) \
        #         .limit(search_results_limit - len(search_shops_startswith)).order_by(Shop.title)
        #     shops_tags = Tag_of_shops.select(Tag_of_shops.shop_id, Tag_of_shops.tag_id, Tag.title) \
        #         .where(Tag_of_shops.shop_id << search_shops_startswith | Tag_of_shops.shop_id << search_shops_contains) \
        #         .join(Tag, on=(Tag_of_shops.tag_id == Tag.id))
        #     for shop in itertools.chain(search_shops_startswith, search_shops_contains):
        #         shop_tags_list = []
        #         for shop_tag in shops_tags:
        #             if shop.id == shop_tag.shop_id:
        #                 shop_tags_list.append({"shop_tag_id": shop_tag.tag_id, "shop_tag_title": shop_tag.tag.title})
        #         shop_dict = model_to_dict(shop)
        #         shop_dict["tags"] = shop_tags_list
        #         search_results.append(shop_dict)
        #     return jsonify({"search_results": search_results}), 200
        # except Exception:
        #     pass
        # offset = (page - 1) * page_limit
        # if len(db_tags) > 0:
        #     shops = Shop.select().offset(offset).limit(page_limit).where(Tag_of_shops.tag_id << db_tags) \
        #         .join(Tag_of_shops, on=(Shop.id == Tag_of_shops.shop_id)).order_by(Shop.title).group_by(Shop.id)
        # else:
        #     shops = Shop.select().offset(offset).limit(page_limit).order_by(Shop.title)
        # shops_tags = Tag_of_shops.select(Tag_of_shops.shop_id, Tag_of_shops.tag_id, Tag.title) \
        #     .where(Tag_of_shops.shop_id << shops).join(Tag, on=(Tag_of_shops.tag_id == Tag.id))
        # for shop in shops:
        #     shop_tags_list = []
        #     for shop_tag in shops_tags:
        #         if shop.id == shop_tag.shop_id:
        #             shop_tags_list.append({"shop_tag_id": shop_tag.tag_id, "shop_tag_title": shop_tag.tag.title})
        #     shop_dict = model_to_dict(shop)
        #     shop_dict["tags"] = shop_tags_list
        #     shops_list.append(shop_dict)
        # return jsonify({"shops": shops_list, "postsOnPage": page_limit}), 200
