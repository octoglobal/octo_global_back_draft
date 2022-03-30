import config
import random
from peewee import fn
from base64 import b64encode
from hashlib import sha256
from database import User


def password_hash(password, privat_salt):
    global_salt = config.global_salt
    hashed_password = str
    for i in range(2):
        hashed_password = b64encode(sha256(str(global_salt + password + str(privat_salt)).encode()).digest()).decode()
        password = hashed_password
    return hashed_password


def get_user_enough_data(user):
    enough_user_data = {}
    enough_keys = [
        "id",
        "personalAreaId",
        "email",
        "phone",
        "addresses",
        "verifiedEmail",
        "name",
        "surname",
        "photo",
        "username",
        "registrationTime",
        "lastLoginTime"]
    for key in enough_keys:
        enough_user_data[key] = user[key]
    return enough_user_data


def check_image_filename(filename):
    if "." in filename:
        if filename.rsplit(".", 1)[-1].lower() in config.images_allowed_formats:
            return True
    return False


def make_personal_area_id():
    minimum_id = 1000000
    id_step = 5000
    max_id = User.select(fn.MAX(User.personalAreaId)).scalar()
    if max_id is None:
        max_id = minimum_id
    max_id = int(max_id)
    id_index = (max_id - minimum_id) // id_step
    left_id = minimum_id + id_step * id_index
    right_id = left_id + id_step - 1
    busy_ids_dict = list(
        User.select(User.personalAreaId).where(User.personalAreaId >= left_id, User.personalAreaId <= right_id).dicts()
    )
    busy_ids_list = [int(temp["personalAreaId"]) for temp in busy_ids_dict]
    from_left_to_right_id_list = list(range(left_id, right_id + 1))
    freedom_ids = [temp for temp in from_left_to_right_id_list if temp not in busy_ids_list]
    if len(freedom_ids) == 0:
        personal_area_id = random.randint(left_id + id_step, right_id + id_step)
    else:
        personal_area_id = random.choice(freedom_ids)
    return personal_area_id
