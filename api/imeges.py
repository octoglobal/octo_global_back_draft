from flask import Blueprint, request, send_file, abort
from functions import images_func


image = Blueprint("image_serv", __name__)


@image.route("/image/<image_hash>", methods=["GET"])
def get_images(image_hash):

    if request.method == "GET":
        try:
            road_to_file = images_func.road_to_file(image_hash)
            return send_file(road_to_file, mimetype="image/gif")
        except Exception:
            return abort(404)
