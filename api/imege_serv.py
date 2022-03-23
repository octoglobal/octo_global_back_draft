from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from PIL import Image
import hashlib
import os
from database import User
from functions import data_ordering
from functions import images_func
import config


image_serv = Blueprint("image_serv", __name__)


@image_serv.route("/image/<image_hash>", methods=["GET"])
def get_images(image_hash):

    if request.method == "GET":
        try:
            road_to_file = images_func.road_to_file(image_hash)
            print(road_to_file)
            return send_file(road_to_file, mimetype="image/gif")
        except Exception:
            return "404", 404


@image_serv.route("/upload_photos", methods=["POST"])
# @jwt_required()
def upload_photos():

    if request.method == "POST":
        # token_data = get_jwt_identity()
        # try:
        #     admin_token_check = token_data["admin"]
        # except Exception:
        #     return "invalid data", 422
        # if not admin_token_check:
        #     return "invalid data", 422
        # user_id = token_data["user_id"]
        # user = User.select().where(User.id == user_id)
        # if not user.exists():
        #     return "user not found", 403
        files = request.files
        photo_roads = []
        if "image" not in request.files:
            return "Bad request", 400
        images = files.getlist("image")
        for image in images:
            filename = image.filename
            if image and data_ordering.check_image_filename(filename):
                try:
                    data = image.read()
                    image_hash = str(hashlib.md5(data).hexdigest())
                    new_filename = image_hash[8:] + ".webp"
                    photo = Image.open(image)
                    photo = photo.convert('RGB')
                    photo.thumbnail(size=(1600, 1600))
                    hash_road = images_func.save_road(image_hash)
                    save_road = config.flask_upload_folder + "/" + hash_road
                    if not os.path.exists(save_road):
                        os.makedirs(save_road)
                    photo.save(save_road + "/" + new_filename, optimize=True, quality=80)
                    photo_roads.append(image_hash)
                except Exception:
                    photo_roads.append(None)
        return jsonify({"photos": photo_roads}), 200
