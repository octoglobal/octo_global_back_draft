from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import config
from api import registration_and_authorization


app = Flask(__name__)
app.register_blueprint(registration_and_authorization.reg_and_auth)
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
