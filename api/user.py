from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from database import User, Users_addresses
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
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True)\
            .order_by(Users_addresses.id.desc()).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})

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
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True)\
            .order_by(Users_addresses.id.desc()).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})


@user_api.route("/user/address", methods=["POST", "DELETE"])
@jwt_required()
def address_info():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            address = str(request_data["address"])
        except Exception:
            return "invalid data", 422
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        Users_addresses.create(userId=user_id, address=address, delete=False, createdTime=datetime.now())
        user = user.get()
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True)\
            .order_by(Users_addresses.id.desc()).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})

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
            .where(Users_addresses.id == address_id, Users_addresses.userId == user_id, Users_addresses.delete != True)
        if not address.exists():
            return "address not found", 403
        address = address.get()
        address.deletedTime = datetime.now()
        address.delete = True
        address.save()
        user = user.get()
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True).dicts() \
            .order_by(Users_addresses.id.desc())
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        return jsonify({"user": enough_user_data})
