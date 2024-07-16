# app/services/auth_service.py
from flask import current_app
from librouteros import connect
from librouteros.login import plain
from librouteros.exceptions import LibRouterosError
from ..utils.jwt_utils import create_token, verify_token

class AuthService:
    @staticmethod
    def connect(data):
        ip_address = data['ip']
        username = data['username']
        password = data['password']
        try:
            connection = connect(host=ip_address, username=username, password=password, login_method=plain)
            connection.close()
            token = create_token({'ip': ip_address, 'username': username, 'password': password})
            return {"status": "OK", "token": token}
        except LibRouterosError as error:
            return {"status": "Error", "message": str(error)}