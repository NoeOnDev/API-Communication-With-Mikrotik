# app/services/user_service.py
from flask import current_app
from librouteros import connect
from librouteros.login import plain
from librouteros.exceptions import LibRouterosError
from ..utils.jwt_utils import verify_token

class UserService:
    @staticmethod
    def get_users(token):
        data = verify_token(token)
        if not data:
            return {"status": "Error", "message": "Invalid or expired token"}

        try:
            connection = connect(host=data['ip'], username=data['username'], password=data['password'], login_method=plain)
            users = list(connection('/user/print'))
            connection.close()
            return {"status": "OK", "users": users}
        except LibRouterosError as error:
            return {"status": "Error", "message": str(error)}
        except Exception as error:
            return {"status": "Error", "message": "General error: " + str(error)}