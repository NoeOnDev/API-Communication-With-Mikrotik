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
        users = list(connection('/user/print'))
        connection.close()
        return jsonify({"status": "OK", "users": users})
    except LibRouterosError as error:
        return jsonify({"status": "Error", "message": str(error)}), 400
    except Exception as error:
        return jsonify({"status": "Error", "message": "General error: " + str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
