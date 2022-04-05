from PIL import Image
import config
import hashlib
import os
from functions import data_ordering


def road_to_file(image_hash):
    return config.flask_upload_folder + "/" + str(image_hash[0:2]) + "/" + str(image_hash[2:4]) + "/" \
           + str(image_hash[4:6]) + "/" + str(image_hash[6:8]) + "/" + str(image_hash[8:]) + ".webp"


def save_road_string(image_hash):
    return image_hash[0:2] + "/" + image_hash[2:4] + "/" + image_hash[4:6] + "/" + image_hash[6:8]


def save_image(image, max_size):
    filename = image.filename
    if not image or not data_ordering.check_image_filename(filename):
        raise Exception
    data = image.read()
    image_hash_md5 = str(hashlib.md5(data).hexdigest())
    image_hash_sha1 = str(hashlib.sha1(data).hexdigest())
    image_hash = image_hash_md5 + image_hash_sha1
    new_filename = image_hash[8:] + ".webp"
    photo = Image.open(image)
    photo = photo.convert('RGB')
    photo.thumbnail(size=(max_size, max_size))
    hash_road = save_road_string(image_hash)
    save_road = config.flask_upload_folder + "/" + hash_road
    if not os.path.exists(save_road):
        os.makedirs(save_road)
    photo.save(save_road + "/" + new_filename, optimize=True, quality=80)
    return image_hash
