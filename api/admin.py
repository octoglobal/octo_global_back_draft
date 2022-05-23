from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from playhouse.shortcuts import model_to_dict
import xlsxwriter
import io
import json
import uuid
from datetime import datetime
from database import Shop, Tag_of_shops, Tag, Review, Post, Post_product, User, Order, Package, \
    Users_addresses, Users_balance_history, Exchange_rate
from functions import images_func, data_ordering, email_sending

admin_api = Blueprint("admin_api", __name__)


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        token_data = get_jwt_identity()
        try:
            admin_token_check = token_data["status"]
        except Exception:
            return "rights error", 406
        if admin_token_check != 9:
            return "rights error", 406
        return func(*args, **kwargs)
    return decorated_function


@admin_api.route("/admin/shop", methods=["POST"])
# @jwt_required()
# @admin_required
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


@admin_api.route("/admin/blog", methods=["POST", "DELETE", "PATCH"])
@jwt_required()
@admin_required
def admin_blog_actions():
    if request.method == "POST":
        request_files = request.files.to_dict(flat=False)
        request_form = request.form.to_dict(flat=False)
        post = {}
        post_products = []
        try:
            request_data_list = request_form["json_data"]
            if len(request_data_list) != 1:
                return "invalid data", 422
            string_request_data = request_data_list[0]
            request_data = json.loads(string_request_data)
            post["title"] = str(request_data["title"])
            post["body"] = str(request_data["body"])
            post_products_check = list(request_data["products"])
            for product_index in range(3):
                post_product = {
                    "title": post_products_check[product_index]["title"],
                    "body": post_products_check[product_index]["body"],
                    "url": post_products_check[product_index]["url"]
                }
                post_products.append(post_product)
        except Exception:
            return "invalid data", 422
        try:
            images_list = request_files["image"]
            if len(images_list) != 3:
                return "invalid data", 422
        except Exception:
            return "invalid data", 422
        products_images = []
        try:
            for image_file in images_list:
                image = images_func.save_image(image_file, 1600)
                products_images.append(image)
        except Exception:
            return "image loading error", 422
        try:
            post = Post.create(
                title=post["title"],
                body=post["body"],
                statusId=0,
                createdTime=datetime.now()
            )
            post_id = int(post.id)
            for index, post_product in enumerate(post_products):
                post_product["postId"] = post_id
                post_product["photo"] = products_images[index]
            Post_product.insert_many(post_products).execute()
        except Exception as e:
            print(e)
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
        Post_product.delete().where(Post_product.postId == blog_id).execute()
        return jsonify({"message": "success"}), 200

    if request.method == "PATCH":
        request_form = request.form.to_dict(flat=False)
        post = {}
        post_products = []
        try:
            request_data_list = request_form["json_data"]
            if len(request_data_list) != 1:
                return "invalid data", 422
            string_request_data = request_data_list[0]
            request_data = json.loads(string_request_data)
            post["title"] = str(request_data["title"])
            post["body"] = str(request_data["body"])
            post["id"] = int(request_data["blogId"])
            post_products_check = list(request_data["products"])
            for product_index in range(3):
                post_product = {
                    "title": post_products_check[product_index]["title"],
                    "body": post_products_check[product_index]["body"],
                    "url": post_products_check[product_index]["url"]
                }
                post_products.append(post_product)
        except Exception:
            return "invalid data", 422
        try:
            Post.update(
                title=post["title"],
                body=post["body"],
                statusId=0,
                editedTime=datetime.now()
            ).where(Post.id == post["id"]).execute()
            exist_post_products = Post_product.select().where(Post_product.postId == post["id"])\
                .order_by(Post_product.id)
            exist_post_products_list = list(exist_post_products.dicts())
            for index, exist_post_product in enumerate(exist_post_products_list):
                exist_post_product_id = exist_post_product["id"]
                Post_product.update(
                    title=post_products[index]["title"],
                    body=post_products[index]["body"],
                    url=post_products[index]["url"]
                ).where(Post_product.id == exist_post_product_id).execute()
        except Exception as e:
            print(e)
            return "internal server error", 500
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
            status_id = int(request_data["statusId"])
            if status_id not in [0, 1]:
                raise
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        order = Order.select().where(Order.userId == user_id, Order.trackNumber == track_number)
        if order.exists():
            order = order.get()
            if order.statusId != status_id:
                method = "patch"
                order.statusId = status_id
                order.trackNumber = track_number
                order.approvalTime = datetime.now()
                order.save()
                if status_id == 1:
                    email_sending.send_arrived_at_the_warehouse(user_id, user.email, "Octo Global: Оповещение",
                                                                user.name, user.surname, order.longId)
            else:
                return "order with this track number and status already exists", 409
        else:
            method = "create"
            long_id = data_ordering.make_order_long_id()
            Order.create(
                userId=user_id,
                longId=long_id,
                title=title,
                comment=comment,
                statusId=status_id,
                trackNumber=track_number,
                createdTime=datetime.now(),
                approvalTime=datetime.now()
            )
            if status_id == 1:
                email_sending.send_arrived_at_the_warehouse(user_id, user.email, "Octo Global: Оповещение",
                                                            user.name, user.surname, order.longId)
        return jsonify({"message": "success", "method": method}), 200

    if request.method == "DELETE":
        request_data = request.get_json()
        try:
            order_id = request_data["orderId"]
            assert isinstance(order_id, list)
            user_id = int(request_data["userId"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403

        # orders = Order.select().where(Order.id << order_id, Order.userId == user_id,
        #                               ((Order.statusId == 0) | (Order.statusId == 1)))
        orders = Order.select().where(Order.id << order_id, Order.userId == user_id,
                                      ((Order.statusId == 0) | (Order.statusId == 1)))
        Order.delete().where(Order.id << orders).execute()
        # order = Order.select().where(Order.id == order_id, Order.userId == user_id,
        #                              ((Order.statusId == 0) | (Order.statusId == 1)))
        # if not order.exists():
        #     return "order not found or has an invalid status", 403
        # order.get().delete_instance()
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
        package_dict = model_to_dict(package)
        return jsonify({"message": "success", "package": package_dict}), 200

    # if request.method == "PATCH":
    #     request_data = request.get_json()
    #     try:
    #         user_id = int(request_data["userId"])
    #         package_id = int(request_data["packageId"])
    #     except Exception:
    #         return "invalid data", 422
    #     user = User.select().where(User.id == user_id)
    #     if not user.exists():
    #         return "user not found", 403
    #     package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 0)
    #     if not package.exists():
    #         return "package not found", 403
    #     package = package.get()
    #     package.statusId = 1
    #     package.agreementToConsolidationTime = datetime.now()
    #     package.save()
    #     return jsonify({"message": "success"}), 200

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
                   ((Package.statusId == 0) | (Package.statusId == 1) |
                    (Package.statusId == 2) | (Package.statusId == 4)))
        if not package.exists():
            return "package not found", 403
        user_orders = Order.select() \
            .where(Order.userId == user_id,
                   Order.statusId == 2,
                   Order.packageId == package_id,
                   Package.id == package_id,
                   Package.userId == user_id,
                   ((Package.statusId == 0) | (Package.statusId == 1) |
                    (Package.statusId == 2) | (Package.statusId == 4))) \
            .join(Package, on=(Order.packageId == Package.id))
        Order.update(statusId=1, packageId=None).where(Order.id << user_orders).execute()
        package.get().delete_instance()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/package_with_orders", methods=["DELETE"])
@jwt_required()
@admin_required
def admin_package_with_orders_actions():

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
            .where(Package.id == package_id, Package.userId == user_id)
        if not package.exists():
            return "package not found", 403
        user_orders = Order.select() \
            .where(Order.userId == user_id,
                   Order.statusId == 2,
                   Order.packageId == package_id,
                   Package.id == package_id,
                   Package.userId == user_id) \
            .join(Package, on=(Order.packageId == Package.id))
        Order.delete().where(Order.id << user_orders).execute()
        package.get().delete_instance()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/package/address", methods=["POST", "DELETE"])
@jwt_required()
@admin_required
def admin_packages_address_actions():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            package_id = request_data["packageId"]
            address_id = request_data["addressId"]
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user_address = Users_addresses.select()\
            .where(Users_addresses.userId == user_id, Users_addresses.id == address_id)
        if not user_address.exists():
            return "address not found", 403
        package = Package.select().where(Package.id == package_id, Package.userId == user_id,
                                         ((Package.statusId == 0) | (Package.statusId == 1) | (Package.statusId == 4)))
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.addressId = address_id
        package.statusId = 2
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
        user = user.get()
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 2)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 4
        package.addressId = None
        package.save()
        email_sending.send_cancelled_package(user_id, user.email, "Octo Global: Оповещение",
                                             user.name, user.surname, package.longId)
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
        user = user.get()
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 2)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 3
        package.trackNumber = track_number
        package.dispatchTime = datetime.now()
        package.save()
        package_address = Users_addresses.select().where(Users_addresses.id == package.addressId).get()
        email_sending.send_package_send(user_id, user.email, "Octo Global: Оповещение",
                                        user.name, user.surname, package.longId, package_address.address_string)
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
        package = Package.select().where(Package.id == package_id, Package.userId == user_id, Package.statusId == 3)
        if not package.exists():
            return "package not found", 403
        package = package.get()
        package.statusId = 2
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


@admin_api.route("/admin/user/<user_id>", methods=["GET", "PATCH"])
@jwt_required()
@admin_required
def admin_user_actions(user_id):
    if request.method == "GET":
        try:
            user_id = int(user_id)
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address_string,
                                                Users_addresses.phone, Users_addresses.name, Users_addresses.surname,
                                                Users_addresses.longitude, Users_addresses.latitude) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True) \
            .order_by(Users_addresses.id).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data}), 200

    if request.method == "PATCH":
        request_data = request.get_json()
        changes = {}
        try:
            user_id = int(user_id)
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()

        try:
            new_email = request_data["email"]
            changes["email"] = True
            if User.get_or_none(email=new_email) is not None:
                changes["email"] = False
                raise Exception
            user.email = new_email
        except Exception:
            pass
        try:
            new_phone = request_data["phone"]
            changes["phone"] = True
            if User.get_or_none(phone=new_phone) is not None:
                changes["phone"] = False
                raise Exception
            user.phone = new_phone
        except Exception:
            pass
        try:
            new_name = request_data["name"]
            changes["name"] = True
            user.name = new_name
        except Exception:
            pass
        try:
            new_surname = request_data["surname"]
            changes["surname"] = True
            user.surname = new_surname
        except Exception:
            pass
        try:
            new_password = request_data["password"]
            changes["password"] = True
            privat_salt = uuid.uuid4().hex
            hashed_password = data_ordering.password_hash(new_password, privat_salt)
            user.password = hashed_password
            user.salt = privat_salt
        except Exception:
            pass
        user.save()
        return jsonify({"message": "success", "changes": changes}), 200


@admin_api.route("/admin/search", methods=["GET"])
# @jwt_required()
# @admin_required
def admin_search_actions():
    if request.method == "GET":
        search_results_limit = 5
        args = request.args.to_dict(flat=False)
        try:
            search_string = str(args["text"][0])
        except Exception:
            return "invalid data", 422
        user_long_id_search = list(User.select(User.personalAreaId, User.id, User.name,
                                               User.surname, User.statusId, User.email)
                                   .where(User.personalAreaId.cast("TEXT").contains(search_string))
                                   .limit(search_results_limit).order_by(User.personalAreaId).dicts())
        user_email_search = list(User.select(User.personalAreaId, User.id, User.name,
                                             User.surname, User.statusId, User.email)
                                 .where(User.email.contains(search_string))
                                 .limit(search_results_limit).order_by(User.email).dicts())

        user_initials_search = list(User.select(User.personalAreaId, User.id, User.name, User.surname,
                                                User.statusId, User.email)
                                    .where((User.name.contains(search_string)) | (User.surname.contains(search_string)))
                                    .limit(search_results_limit).order_by(User.surname).dicts())
        order_long_id_search = list(Order.select(Order.longId, Order.id, Order.title, Order.comment,
                                                 Order.trackNumber, Order.statusId, Order.userId,
                                                 User.id.alias("userId"), User.email.alias("userEmail"),
                                                 User.name.alias("userName"), User.personalAreaId.alias("userAreaId"),
                                                 User.statusId.alias("userStatusId"), User.surname.alias("userSurname"))
                                    .where(Order.longId.cast("TEXT").contains(search_string))
                                    .join(User, on=(Order.userId == User.id))
                                    .limit(search_results_limit).order_by(Order.longId).dicts())
        order_track_number_search = list(Order.select(Order.longId, Order.id, Order.title, Order.comment,
                                                      Order.trackNumber, Order.statusId, Order.userId,
                                                      User.id.alias("userId"), User.email.alias("userEmail"),
                                                      User.name.alias("userName"),
                                                      User.personalAreaId.alias("userAreaId"),
                                                      User.statusId.alias("userStatusId"),
                                                      User.surname.alias("userSurname"))
                                         .where(Order.trackNumber.contains(search_string))
                                         .join(User, on=(Order.userId == User.id))
                                         .limit(search_results_limit).order_by(Order.trackNumber).dicts())
        search_results = {
            "users_numbers": user_long_id_search,
            "users_emails": user_email_search,
            "orders_numbers": order_long_id_search,
            "orders_track_numbers": order_track_number_search,
            "user_initials_search": user_initials_search
        }
        return jsonify({"search_results": search_results}), 200


@admin_api.route("/admin/user/address", methods=["POST", "DELETE"])
@jwt_required()
@admin_required
def admin_address_info():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            name = str(request_data["name"])
            surname = str(request_data["surname"])
            address_string = str(request_data["address_string"])
            latitude = str(request_data["latitude"])
            longitude = str(request_data["longitude"])
            phone = str(request_data["phone"])
        except Exception:
            return "invalid data", 422
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
            user_id = int(request_data["userId"])
            address_id = str(request_data["address_id"])
        except Exception:
            return "invalid data", 422
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


@admin_api.route("/admin/user/orders/expected", methods=["GET"])
@jwt_required()
@admin_required
def admin_orders_expected_info():

    if request.method == "GET":
        args = request.args.to_dict(flat=False)
        try:
            user_id = int(args["userId"][0])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403

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


@admin_api.route("/admin/user/orders/are_waiting", methods=["GET"])
@jwt_required()
@admin_required
def admin_orders_are_waiting_info():

    if request.method == "GET":
        args = request.args.to_dict(flat=False)
        try:
            user_id = int(args["userId"][0])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
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


@admin_api.route("/admin/user/orders/sent", methods=["GET"])
@jwt_required()
@admin_required
def admin_orders_sent_info():

    if request.method == "GET":
        args = request.args.to_dict(flat=False)
        try:
            user_id = int(args["userId"][0])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
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


@admin_api.route("/admin/user/balance", methods=["POST"])
# @jwt_required()
# @admin_required
def admin_balance_change():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            user_id = int(request_data["userId"])
            amount = int(request_data["amount"])
            comment = str(request_data["comment"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        try:
            user = user.get()
            if user.balance is None:
                new_balance = amount
            else:
                new_balance = user.balance + amount
            user.balance = new_balance
            if new_balance < 0:
                return "insufficient funds in the account", 400
            print(user.balance)
            user.save()
            Users_balance_history.create(
                userId=user_id,
                amount=amount,
                comment=comment,
                createdTime=datetime.now()
            )
        except Exception as e:
            print(e)
            return "balance error", 500
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/user/<user_id>/balance_history", methods=["GET"])
@jwt_required()
@admin_required
def admin_user_balance_history(user_id):

    if request.method == "GET":
        try:
            user_id = int(user_id)
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        balance = user.balance
        if balance is None:
            balance = 0
        balance_history = Users_balance_history.select().where(Users_balance_history.userId == user_id)\
            .order_by(Users_balance_history.id.desc()).limit(50).dicts()
        return jsonify({"balance_history": list(balance_history), "balance": balance}), 200


@admin_api.route("/admin/exchange_rate", methods=["POST"])
@jwt_required()
@admin_required
def admin_exchange_rate():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            currency = str(request_data["currency"])
            value = int(request_data["value"])
        except Exception:
            return "invalid data", 422
        currency = Exchange_rate.select().where(Exchange_rate.currency == currency)
        if not currency.exists():
            return "currency not found", 403
        try:
            currency = currency.get()
            currency.value = value
            currency.save()
        except Exception:
            return "currency error", 500
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/all_expected", methods=["GET"])
@jwt_required()
@admin_required
def admin_all_are_waiting():

    if request.method == "GET":
        args = request.args.to_dict(flat=False)
        try:
            page = int(args["page"][0])
            if page <= 0:
                raise
        except Exception:
            page = 1
        try:
            page_limit = int(args["page_limit"][0])
            if page_limit <= 0 or page_limit > 100:
                raise
        except Exception:
            page_limit = 30
        offset = (page - 1) * page_limit
        all_expected_orders = list(Order.select(Order.id.alias("orderId"), Order.longId.alias("orderLongId"),
                                                Order.trackNumber.alias("orderTrackNumber"), User.id.alias("userId"),
                                                Order.invoice_check.alias("orderInvoiceCheck"),
                                                User.personalAreaId.alias("userPersonalAreaId"),
                                                User.email.alias("userEmail"), User.name.alias("userName"),
                                                User.surname.alias("userSurname"))
                                   .join(User, on=(Order.userId == User.id))
                                   .where(Order.statusId == 0)
                                   .order_by(Order.id.desc()).offset(offset).limit(page_limit).dicts())
        for order in all_expected_orders:
            if order["orderInvoiceCheck"] is None:
                order["orderInvoiceCheck"] = False
        return jsonify({"orders": all_expected_orders}), 200


@admin_api.route("/admin/invoice_check", methods=["POST"])
@jwt_required()
@admin_required
def admin_invoice_check():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            order_id = request_data["orderId"]
            invoice_check = request_data["invoice_check"]
            if invoice_check not in [True, False]:
                raise
        except Exception:
            return "invalid data", 422
        invoice_check = bool(invoice_check)
        order = Order.select().where(Order.id == order_id, Order.statusId == 0)
        if not order.exists():
            return "order not found", 403
        order = order.get()
        order.invoice_check = invoice_check
        order.save()
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/users_table", methods=["GET"])
@jwt_required()
@admin_required
def admin_get_table():

    if request.method == "GET":
        row = 0
        users = list(User.select().where(User.statusId != 9).order_by(User.id).dicts())
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Users")
        worksheet.write(row, 0, "Account №")
        worksheet.write(row, 1, "Email")
        worksheet.write(row, 2, "Phone")
        worksheet.write(row, 3, "Name")
        worksheet.write(row, 4, "Surname")
        worksheet.write(row, 5, "Balance")
        worksheet.write(row, 6, "Registration time")
        worksheet.write(row, 7, "Last login time")
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 4, 20)
        worksheet.set_column(5, 5, 10)
        worksheet.set_column(6, 7, 20)
        row += 1
        for user in users:
            if user["balance"] is None:
                user["balance"] = 0
            worksheet.write(row, 0, user["personalAreaId"])
            worksheet.write(row, 1, user["email"])
            worksheet.write(row, 2, user["phone"])
            worksheet.write(row, 3, user["name"])
            worksheet.write(row, 4, user["surname"])
            worksheet.write(row, 5, float('{:.2f}'.format(int(user["balance"]) / 100)))
            try:
                worksheet.write(row, 6, user["registrationTime"].strftime("%m/%d/%Y, %H:%M"))
            except Exception:
                worksheet.write(row, 6, user["registrationTime"])
            try:
                worksheet.write(row, 7, user["lastLoginTime"].strftime("%m/%d/%Y, %H:%M"))
            except Exception:
                worksheet.write(row, 7, user["lastLoginTime"])
            row += 1
        workbook.close()
        output.seek(0)
        # output.close()
        return send_file(output, as_attachment=True, attachment_filename="Octo Global users.xlsx",
                         mimetype="application/vnd.ms-excel")
