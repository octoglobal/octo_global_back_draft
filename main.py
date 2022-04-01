from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import config
from api.registration_and_authorization import reg_and_auth
from api.imege_serv import image_serv
from api.user import user_api
from api.admin import admin_api


app = Flask(__name__, static_url_path=config.static_url_path)
app.register_blueprint(admin_api)
app.register_blueprint(reg_and_auth)
app.register_blueprint(user_api)
app.register_blueprint(image_serv)
jwt = JWTManager(app)
CORS(app, supports_credentials=config.supports_credentials)
app.config["SECRET_KEY"] = config.flask_secret_key
app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=config.jwt_access_token_expires_minutes)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=config.jwt_refresh_token_expires_days)
app.config["JWT_TOKEN_LOCATION"] = [config.jwt_token_location]
app.config["JWT_COOKIE_SECURE"] = config.jwt_cookie_secure
app.config["JWT_COOKIE_CSRF_PROTECT"] = config.jwt_cookie_csrf_protect
app.config["JWT_CSRF_CHECK_FORM"] = config.jwt_csrf_check_form
app.config["JWT_SESSION_COOKIE"] = config.jwt_session_cookie
global_salt = config.global_salt


@app.route("/ver", methods=["GET"])
def version():
    if request.method == "GET":
        return jsonify({"message": "version 0.001"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
