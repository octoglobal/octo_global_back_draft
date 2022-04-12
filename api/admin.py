from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import json
from datetime import datetime
from database import Shop, Tag_of_shops, Tag, Review, Post, Post_photo
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
        except Exception:
            return "internal server error", 500
        return jsonify({"message": "success"}), 200


@admin_api.route("/admin/review", methods=["DELETE"])
@jwt_required()
# @admin_required
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
# @admin_required
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
