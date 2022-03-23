import config
from base64 import b64encode
from hashlib import sha256


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
        "email",
        "phone",
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
