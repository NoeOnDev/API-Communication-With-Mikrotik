from flask import current_app
from librouteros import connect
from librouteros.login import plain
from librouteros.exceptions import LibRouterosError
from ..utils.jwt_utils import verify_token

class ManagementService:
    @staticmethod
    def delete_user(token, user_id):
        if not token:
            return {"status": "Error", "message": "Missing token"}, 400

        data = verify_token(token)
        if not data:
            return {"status": "Error", "message": "Invalid or expired token"}, 400

        if not user_id:
            return {"status": "Error", "message": "Missing user id"}, 400

        try:
            connection = connect(
                host=data['ip'],
                username=data['username'],
                password=data['password'],
                login_method=plain,
            )
            current_app.logger.info('Connection established')
            current_app.logger.info(f"Attempting to delete user with ID: {user_id}")

            users = connection.path('/user')
            users.remove(user_id)

            current_app.logger.info(f"User {user_id} deleted")

            remaining_users = list(users)
            if any(user['.id'] == user_id for user in remaining_users):
                current_app.logger.error(f"User {user_id} still exists after deletion attempt")
                connection.close()
                return {"status": "Error", "message": f"Failed to delete user {user_id}"}, 400

            connection.close()
            return {"status": "OK", "message": f"User {user_id} deleted"}
        except LibRouterosError as error:
            current_app.logger.error(f"LibRouterosError: {error}")
            return {"status": "Error", "message": str(error)}, 400
        except Exception as error:
            current_app.logger.error(f"General error: {error}")
            return {"status": "Error", "message": "General error: " + str(error)}, 500

    @staticmethod
    def add_user(token, user_data):
        if not token:
            return {"status": "Error", "message": "Missing token"}, 400

        data = verify_token(token)
        if not data:
            return {"status": "Error", "message": "Invalid or expired token"}, 400

        current_app.logger.info('Received user data: %s', user_data)

        username = user_data.get('name')
        password = user_data.get('password')
        group = user_data.get('group', 'read')
        comment = user_data.get('comment', '')
        enabled = user_data.get('enabled', True)
        allowed_address = user_data.get('allowedAddress', '')
        inactivity_timeout = user_data.get('inactivityTimeout', '10m')
        inactivity_policy = user_data.get('inactivityPolicy', 'none')

        if not username or not password:
            return {"status": "Error", "message": "Username and password are required"}, 400

        try:
            connection = connect(
                host=data['ip'],
                username=data['username'],
                password=data['password'],
                login_method=plain,
            )
            current_app.logger.info('Connection established')

            users = connection.path('/user')
            user_details = {
                'name': username,
                'password': password,
                'group': group,
                'comment': comment,
                'disabled': not enabled,
                'address': allowed_address if allowed_address else "",
                'inactivity-timeout': inactivity_timeout,
                'inactivity-policy': inactivity_policy,
            }

            new_user_id = users.add(**user_details)

            current_app.logger.info(f"User {username} added with ID {new_user_id}")
            connection.close()
            return {"status": "OK", "message": f"User {username} added", "id": new_user_id}
        except LibRouterosError as error:
            current_app.logger.error(f"LibRouterosError: {error}")
            return {"status": "Error", "message": str(error)}, 400
        except Exception as error:
            current_app.logger.error(f"General error: {error}")
            return {"status": "Error", "message": "General error: " + str(error)}, 500
