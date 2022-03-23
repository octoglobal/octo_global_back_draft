from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from playhouse.shortcuts import model_to_dict
from database import User
from functions import data_ordering


user_api = Blueprint("user_api", __name__)


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
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user = model_to_dict(user)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})
