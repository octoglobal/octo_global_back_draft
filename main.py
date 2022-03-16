from flask import Flask, request, jsonify, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, JWTManager, get_jwt_identity
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
# import json
# from peewee import fn

import config
# from database import User, Order, News, Shop


app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)

app.config["SECRET_KEY"] = config.flask_secret_key
app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=360)
global_salt = config.global_salt


@app.route("/ver", methods=["GET"])
def version():
    if request.method == "GET":
        return jsonify({"message": "version 0.001"}), 200


@app.route("/registration", methods=["POST"])
def registration():
    if request.method == "POST":
        request_data = request.get_json()
        try:
            name = request_data["name"]
            surname = request_data["surname"]
            email = request_data["email"]
        except Exception:
            return abort(403)



        return "qweqwe"




















if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
