from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import json
from database import Shop
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
        except Exception:
            return "invalid data", 422
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

        print(photo)
        print(logo)

        # Shop.create(
        #     alias=alias,
        #     title=title,
        #     description=description,
        #     photo=photo,
        #     logo=logo,
        #     priceId=price_id,
        #     url=url
        # )
        return jsonify({"message": "success"}), 200
