# app/utils/jwt_utils.py
import datetime
import jwt
from flask import current_app

def create_token(data):
    return jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), **data}, current_app.config['SECRET_KEY'], algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
