from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from database import User, Users_addresses, Order
from functions import data_ordering

admin_api = Blueprint("admin_api", __name__)


@admin_api.route("/admin", methods=["GET"])
def admin():
    if request.method == "GET":
        return "Admin", 200
