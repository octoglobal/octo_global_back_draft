from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
# from playhouse.shortcuts import model_to_dict
# from datetime import datetime
# from database import User, Users_addresses, Order
# from functions import data_ordering

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


@admin_api.route("/admin/123", methods=["GET"])
@jwt_required()
@admin_required
def admin():
    if request.method == "GET":
        return jsonify({"message": "u Admin"}), 200

