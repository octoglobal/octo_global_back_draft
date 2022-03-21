import config


def road_to_file(image_hash):
    return config.flask_upload_folder + "/" + str(image_hash[0:2]) + "/" + str(image_hash[2:4]) + "/" \
           + str(image_hash[4:6]) + "/" + str(image_hash[6:8]) + "/" + str(image_hash[8:]) + ".webp"


def save_road(image_hash):
    return image_hash[0:2] + "/" + image_hash[2:4] + "/" + image_hash[4:6] + "/" + image_hash[6:8]
