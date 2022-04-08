from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import json
from database import Shop, Tag_of_shops, Tag
from functions import images_func


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


#  Проверить на включенный @admin_required
#  Проверить на включенный @admin_required
#  Проверить на включенный @admin_required
#  Проверить на включенный @admin_required


@admin_api.route("/admin/shop", methods=["POST"])
@jwt_required()
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
        except Exception as e:
            print(e)
            return "internal server error", 500
        return jsonify({"message": "success"}), 200





@admin_api.route("/admin/shop111", methods=["POST"])
# @jwt_required()
# @admin_required
def admin_shop_actions1():
    if request.method == "POST":
        request_files = request.files.to_dict(flat=False)
        request_form = request.form.to_dict(flat=False)

        print(request_files)
        print(request_form)

        alias = None
        title = None
        description = None
        price_id = None
        url = None

        try:
            url = request_form["url"][0]
            tags = request_form["tags"]
            title = request_form["title"]
            if type(tags) != list:
                return "invalid data", 422
            project_tags = list(Tag.select().dicts())
            project_tags = [temp["id"] for temp in project_tags]
            for tag in tags:
                tag = int(tag)
                if type(tag) != int or tag <= 0 or len(tags) != len(set(tags)) or tag not in project_tags:
                    return "invalid data", 422
        except Exception:
            return "ERROR", 405

        image_file = False
        logo_file = False
        photo = None
        logo = None

        try:
            image_list = request_files["image"]
            if len(image_list) != 1:
                return "invalid data", 422
            image_file = image_list[0]
        except Exception:
            pass

        try:
            logo_list = request_files["logo"]
            if len(logo_list) != 1:
                return "invalid data", 422
            logo_file = logo_list[0]
        except Exception:
            pass

        if image_file:
            try:
                photo = images_func.save_image(image_file, 1600)
            except Exception:
                return "image loading error", 422
        if logo_file:
            try:
                logo = images_func.save_image(logo_file, 500)
            except Exception as e:
                print(e)
                return "image loading error", 422
        try:
            print(alias)
            print(title)
            print(description)
            print(price_id)
            print(url)
            print(photo)
            print(logo)
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

        except Exception as e:
            print(e)
            return "internal server error", 500
        return jsonify({"message": "success"}), 200
