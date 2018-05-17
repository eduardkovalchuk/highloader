import jwt
import models
from functools import wraps
from flask import request, jsonify

import main


def token_protected(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        access_token = None
        if 'x-access-token' in request.headers:
            access_token = request.headers['x-access-token']
        else:
            return jsonify({"message": "Access token is missing"}), 401
        try:
            user_data = jwt.decode(access_token, main.app.config["SECRET_KEY"])
            user = models.User.query.filter_by(username=user_data["username"]).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Access token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid access token"}), 401

        return func(user, *args, **kwargs)

    return decorated