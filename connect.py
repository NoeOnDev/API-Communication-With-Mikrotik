import os
from dotenv import load_dotenv
import datetime
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from librouteros import connect
from librouteros.login import plain
from librouteros.exceptions import LibRouterosError

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def create_token(data):
    return jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), **data}, app.config['SECRET_KEY'], algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

@app.route('/connect', methods=['POST'])
def connect_route():
    data = request.get_json()
    ip_address = data['ip']
    username = data['username']
    password = data['password']

    try:
        connection = connect(
            host=ip_address,
            username=username,
            password=password,
            login_method=plain,
        )
        connection.close()
        token = create_token({'ip': ip_address, 'username': username, 'password': password})
        return jsonify({"status": "OK", "token": token})
    except LibRouterosError as error:
        return jsonify({"status": "Error", "message": str(error)}), 400

@app.route('/users', methods=['POST'])
def get_users():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "Error", "message": "Missing token"}), 400

    data = verify_token(token)
    if not data:
        return jsonify({"status": "Error", "message": "Invalid or expired token"}), 400

    try:
        connection = connect(
            host=data['ip'],
            username=data['username'],
            password=data['password'],
            login_method=plain,
        )
        app.logger.info('Connection established')
        users = list(connection('/user/print'))
        app.logger.info(f"Users: {users}")
        connection.close()
        return jsonify({"status": "OK", "users": users})
    except LibRouterosError as error:
        return jsonify({"status": "Error", "message": str(error)}), 400
    except Exception as error:
        return jsonify({"status": "Error", "message": "General error: " + str(error)}), 500

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "Error", "message": "Missing token"}), 400

    data = verify_token(token)
    if not data:
        return jsonify({"status": "Error", "message": "Invalid or expired token"}), 400

    user_id = request.json.get('id')
    if not user_id:
        return jsonify({"status": "Error", "message": "Missing user id"}), 400

    try:
        connection = connect(
            host=data['ip'],
            username=data['username'],
            password=data['password'],
            login_method=plain,
        )
        app.logger.info('Connection established')
        app.logger.info(f"Attempting to delete user with ID: {user_id}")
        
        users = connection.path('/user')
        users.remove(user_id)
        
        app.logger.info(f"User {user_id} deleted")

        remaining_users = list(users)
        if any(user['.id'] == user_id for user in remaining_users):
            app.logger.error(f"User {user_id} still exists after deletion attempt")
            connection.close()
            return jsonify({"status": "Error", "message": f"Failed to delete user {user_id}"}), 400
        
        connection.close()
        return jsonify({"status": "OK", "message": f"User {user_id} deleted"})
    except LibRouterosError as error:
        app.logger.error(f"LibRouterosError: {error}")
        return jsonify({"status": "Error", "message": str(error)}), 400
    except Exception as error:
        app.logger.error(f"General error: {error}")
        return jsonify({"status": "Error", "message": "General error: " + str(error)}), 500

@app.route('/add_user', methods=['POST'])
def add_user():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "Error", "message": "Missing token"}), 400

    data = verify_token(token)
    if not data:
        return jsonify({"status": "Error", "message": "Invalid or expired token"}), 400

    user_data = request.get_json()
    app.logger.info('Received user data: %s', user_data)

    username = user_data.get('name')
    password = user_data.get('password')
    group = user_data.get('group', 'read')
    comment = user_data.get('comment', '')
    enabled = user_data.get('enabled', True)
    allowed_address = user_data.get('allowedAddress', '')

    if not username or not password:
        return jsonify({"status": "Error", "message": "Username and password are required"}), 400

    try:
        connection = connect(
            host=data['ip'],
            username=data['username'],
            password=data['password'],
            login_method=plain,
        )
        app.logger.info('Connection established')
        
        users = connection.path('/user')
        new_user_id = users.add(
            name=username, 
            password=password, 
            group=group, 
            comment=comment, 
            disabled=not enabled,
            address=allowed_address if allowed_address else "",
        )
        
        app.logger.info(f"User {username} added with ID {new_user_id}")
        connection.close()
        return jsonify({"status": "OK", "message": f"User {username} added", "id": new_user_id})
    except LibRouterosError as error:
        app.logger.error(f"LibRouterosError: {error}")
        return jsonify({"status": "Error", "message": str(error)}), 400
    except Exception as error:
        app.logger.error(f"General error: {error}")
        return jsonify({"status": "Error", "message": "General error: " + str(error)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
