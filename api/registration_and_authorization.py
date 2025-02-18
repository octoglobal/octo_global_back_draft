from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from playhouse.shortcuts import model_to_dict
from datetime import datetime, timedelta
import uuid
from database import User, Email_message, Users_addresses
from functions import data_ordering, email_sending


reg_and_auth = Blueprint("reg_and_auth", __name__)


@reg_and_auth.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    if request.method == "GET":
        identity = get_jwt_identity()
        user_id = identity["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user_status = user.statusId
        if user_status == 1:
            return "rights error", 406
        access_token = create_access_token(identity=get_jwt_identity())
        response = jsonify({"message": "success"})
        set_access_cookies(response, access_token)
        return response, 200


@reg_and_auth.route("/registration", methods=["POST"])
def registration():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            email = str(request_data["email"]).lower().replace(" ", "")
            name = str(request_data["name"])
            surname = str(request_data["surname"])
            password = str(request_data["password"])
        except Exception:
            return "invalid data", 422
        personal_area_id = data_ordering.make_personal_area_id()
        if User.get_or_none(email=email) is not None:
            return "user with this email already exists", 409
        privat_salt = uuid.uuid4().hex
        email_token = uuid.uuid4().hex
        hashed_password = data_ordering.password_hash(password, privat_salt)
        try:
            new_user = User.create(
                personalAreaId=personal_area_id,
                email=email,
                name=name,
                surname=surname,
                password=hashed_password,
                salt=privat_salt,
                email_token=email_token,
                verifiedEmail=False,
                registrationTime=datetime.now(),
                statusId=0
            )
        except Exception:
            return "internal server error", 500
        email_result = email_sending.send_welcome_message(new_user.id, email, "Добро пожаловать в Octo Global!",
                                                          email_token, name, surname)
        if not email_result:
            return jsonify({"message": "user successfully created", "sendEmail": False}), 201
        return jsonify({"message": "user successfully created", "sendEmail": True}), 201


@reg_and_auth.route("/login", methods=["GET"])
def login():

    if request.method == "GET":
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return "invalid data", 422
        email = str(auth.username).lower().replace(" ", "")
        password = auth.password
        user = User.select().where(User.email == email)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user_status = user.statusId
        if user_status == 1:
            return "rights error", 406
        user.lastLoginTime = datetime.now()
        user.save()
        privat_salt = user.salt
        db_hashed_password = user.password
        user_id = user.id
        user_status = int(user.statusId)
        hashed_password = data_ordering.password_hash(password, privat_salt)
        if db_hashed_password != hashed_password:
            return "wrong password", 403
        identify = {"user_id": user_id, "status": user_status, "salt": privat_salt}
        # identify = {"user_id": user_id, "status": user_status}
        access_token = create_access_token(identity=identify)
        refresh_token = create_refresh_token(identity=identify)
        user = model_to_dict(user)
        user_addresses = Users_addresses.select(Users_addresses.id, Users_addresses.address_string,
                                                Users_addresses.phone, Users_addresses.name, Users_addresses.surname,
                                                Users_addresses.longitude, Users_addresses.latitude) \
            .where(Users_addresses.userId == user_id, Users_addresses.delete != True)\
            .order_by(Users_addresses.id).dicts()
        user["addresses"] = list(user_addresses)
        enough_user_data = data_ordering.get_user_enough_data(user)
        response = jsonify({"user": enough_user_data})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200


@reg_and_auth.route("/send_verification_message", methods=["GET"])
@jwt_required()
def send_verification_message():

    if request.method == "GET":
        token_data = get_jwt_identity()
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        name = str(user.name)
        surname = str(user.surname)
        email = user.email
        email_token = user.email_token
        time = datetime.now() - timedelta(minutes=60)
        recovery_list = list(Email_message.select().where(Email_message.recipient == email,
                                                          Email_message.date >= time).dicts())
        if len(recovery_list) >= 5:
            return "too many requests", 429
        if not email_sending.send_verification_message(user.id, email, "Octo Global: Подтверждение E-mail",
                                                       email_token, name, surname):
            return "internal server error", 500
        return jsonify({"message": "message sent successfully"}), 200


@reg_and_auth.route("/send_recovery_message", methods=["POST"])
def send_recovery_message():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            email = str(request_data["email"]).lower().replace(" ", "")
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.email == email)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user_id = user.id
        name = str(user.name)
        surname = str(user.surname)
        time = datetime.now() - timedelta(minutes=60)
        recovery_list = list(Email_message.select().where(Email_message.recipient == email,
                                                          Email_message.date >= time).dicts())
        if len(recovery_list) >= 5:
            return "too many requests", 429
        time_limit = datetime.utcnow() + timedelta(minutes=30)
        identify = {"user_id": user_id, "status": 5}
        access_token = create_access_token(identity=identify)
        if not email_sending.send_recovery_message(user_id, email, "Octo Global: Восстановление пароля",
                                                   time_limit, access_token, name, surname):
            return "internal server error", 500
        return jsonify({"message": "message sent successfully"}), 200


@reg_and_auth.route("/mail_confirmation", methods=["POST"])
def mail_confirmation():

    if request.method == "POST":
        request_data = request.get_json()
        try:
            email = str(request_data["email"]).lower().replace(" ", "")
            email_token = str(request_data["emailToken"])
        except Exception:
            return "invalid data", 422
        user = User.select().where(User.email == email, User.email_token == email_token)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        user.verifiedEmail = True
        user.save()
        return jsonify({"message": "mail successfully verified"}), 200


@reg_and_auth.route("/password_change", methods=["POST"])
@jwt_required()
def password_change():

    if request.method == "POST":
        token_data = get_jwt_identity()
        request_data = request.get_json()
        try:
            old_password = str(request_data["old_password"])
            new_password = str(request_data["new_password"])
        except Exception:
            return "invalid data", 422
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        old_privat_salt = user.salt
        db_hashed_password = user.password
        hashed_password = data_ordering.password_hash(old_password, old_privat_salt)
        if db_hashed_password != hashed_password:
            return "wrong password", 403
        new_privat_salt = uuid.uuid4().hex
        new_hashed_password = data_ordering.password_hash(new_password, new_privat_salt)
        user.password = new_hashed_password
        user.salt = new_privat_salt
        user.save()
        identify = {"user_id": user_id, "status": user.statusId, "salt": new_privat_salt}
        access_token = create_access_token(identity=identify)
        refresh_token = create_refresh_token(identity=identify)
        response = jsonify({"message": "password successfully changed"})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200


@reg_and_auth.route("/password_recovery", methods=["POST"])
@jwt_required(locations=["headers"])
def password_recovery():

    if request.method == "POST":
        token_data = get_jwt_identity()
        request_data = request.get_json()
        try:
            recovery_token_check = token_data["status"]
            new_password = str(request_data["password"])
        except Exception:
            return "invalid data", 422
        if recovery_token_check != 5:
            return "invalid data", 422
        user_id = token_data["user_id"]
        user = User.select().where(User.id == user_id)
        if not user.exists():
            return "user not found", 403
        user = user.get()
        old_privat_salt = user.salt
        db_hashed_password = user.password
        old_hashed_password = data_ordering.password_hash(new_password, old_privat_salt)
        if db_hashed_password == old_hashed_password:
            return "old and new passwords must be different", 409
        new_privat_salt = uuid.uuid4().hex
        new_hashed_password = data_ordering.password_hash(new_password, new_privat_salt)
        user.password = new_hashed_password
        user.salt = new_privat_salt
        user.save()
        return jsonify({"message": "password successfully recover"}), 200


@reg_and_auth.route("/logout", methods=["GET"])
def logout():

    if request.method == "GET":
        response = jsonify({"message": "success"})
        unset_jwt_cookies(response)
        return response, 200
