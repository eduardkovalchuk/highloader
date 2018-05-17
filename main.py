import os
import datetime
import jwt
from functools import wraps
from flask import Flask, request, jsonify, abort, make_response, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

import config, controllers, models
from wrapers import token_protected


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'high_loader_db.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')



API = config.API
REGISTER = config.REGISTER
LOGIN = config.LOGIN
UPLOAD = config.UPLOAD
DOWNLOAD = config.DOWNLOAD

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = b'2698aca4a9c3d1b433c5e70852570f85e31a8fb0c33cb6ec'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)


@app.route(API + REGISTER, methods=["POST"])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        return jsonify({"message":"Data missing"}, 206)
    if models.User.query.filter_by(username = username).first():
        return jsonify({"message": "User with this username exists"}), 200
    user = models.User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"username":username}), 201


@app.route(API + LOGIN, methods=["POST"])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({"message":"Some data missing"}), 206
    user = models.User.query.filter_by(username = username).first()
    if user is not None and user.check_password(password):
        access_token = jwt.encode({"username":username, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config["SECRET_KEY"])
        return jsonify({"access_token": access_token.decode('UTF-8')})
    return make_response("Waiting for authenticate!", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})


@app.route(API + UPLOAD, methods=["POST"])
@token_protected
def upload(user):
    if 'file' not in request.files:
        return jsonify({"message":"File is missing"}), 204
    upload_file = request.files['file']
    if upload_file.filename == '':
        return jsonify({"message":"No file selected"}), 206
    if upload_file:
        filename = secure_filename(upload_file.filename)
        print(filename)
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message":"File has been uploaded by " + user.username}), 202
    return jsonify({"message":"Waiting for upload!"}), 200


@app.route("/api/download/<path:filename>", methods=["GET"])
@token_protected
def download(user, filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)