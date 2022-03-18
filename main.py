from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import config
from api.registration_and_authorization import reg_and_auth
from api.imege_serv import image_serv


app = Flask(__name__)
app.register_blueprint(reg_and_auth)
app.register_blueprint(image_serv)
jwt = JWTManager(app)
CORS(app)
app.config["SECRET_KEY"] = config.flask_secret_key
app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=40)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=360)
global_salt = config.global_salt


@app.route("/ver", methods=["GET"])
def version():
    if request.method == "GET":
        return jsonify({"message": "version 0.001"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
