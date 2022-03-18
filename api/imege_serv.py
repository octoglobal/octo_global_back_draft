from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from PIL import Image
import hashlib
import os
from database import User
from functions import data_ordering


image_serv = Blueprint("image_serv", __name__)


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
                    hash_road = image_hash[0:2] + "/" + image_hash[2:4] + "/" + image_hash[4:6] + "/" + image_hash[6:8]
                    # save_road = config.upload_folder + "/" + config.post_alias + "/" + hash_road



                    print(hash_road)
                    # if not os.path.exists(save_road):
                    #     os.makedirs(save_road)


                except Exception:
                    photo_roads.append(None)


        print(photo_roads)
        return "123123"



        new_filename = str(post_id) + file_hash[8:] + ".webp"
        db_filename = file_hash
        hash_road = str(file_hash[0:2]) + "/" + str(file_hash[2:4]) + "/" + str(file_hash[4:6]) + "/" + str(file_hash[6:8])
        save_road = config.upload_folder + "/" + config.post_alias + "/" + hash_road

        if not os.path.exists(save_road):
            os.makedirs(save_road)

        photo = Image.open(file)
        photo = photo.convert('RGB')
        images_functions.resize_thumbnail(photo, 1200, 1200)
        medium_image = photo.copy()
        small_image = photo.copy()
        smallest_image = photo.copy()
        images_functions.make_watermark(photo)
        images_functions.resize_thumbnail(medium_image, 950, 500)
        images_functions.make_watermark(medium_image)
        images_functions.resize_thumbnail(small_image, 400, 400)
        images_functions.resize_thumbnail(smallest_image, 150, 150)
        images_functions.save_image(photo, save_road + "/" + "n" + new_filename, 80)
        images_functions.save_image(medium_image, save_road + "/" + "m" + new_filename, 80)
        images_functions.save_image(small_image, save_road + "/" + "s" + new_filename, 80)
        images_functions.save_image(smallest_image, save_road + "/" + "x" + new_filename, 80)
        db_road = "1/" + config.post_alias + "/" + post_id + "/n/" + db_filename
        photos.append(db_road)
        db_photos.append(db_filename)
