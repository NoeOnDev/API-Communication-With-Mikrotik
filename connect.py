from flask import Flask, request, jsonify
import librouteros
from librouteros.login import plain
from librouteros.exceptions import LibRouterosError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    ip_address = data['ip']
    username = data['username']
    password = data['password']

    try:
        connection = librouteros.connect(
            host=ip_address,
            username=username,
            password=password,
            login_method=plain,
        )
        connection.close()
        return jsonify({"status": "OK"})
    except LibRouterosError as error:
        return jsonify({"status": "Error", "message": str(error)}), 400

@app.route('/users', methods=['POST'])
def get_users():
    data = request.get_json()
    ip_address = data['ip']
    username = data['username']
    password = data['password']

    app.logger.info(f"Attempting to connect to {ip_address} with username {username}")
    try:
        connection = librouteros.connect(
            host=ip_address,
            username=username,
            password=password,
            login_method=plain,
        )
        app.logger.info(f"Connection to {ip_address} successful")
        users = list(connection('/user/print'))
        app.logger.info(f"Users data: {users}")  # Log the users data
        connection.close()
        return jsonify({"status": "OK", "users": users})
    except LibRouterosError as error:
        app.logger.error(f"LibRouterosError: {error}")
        return jsonify({"status": "Error", "message": str(error)}), 400
    except Exception as error:
        app.logger.error(f"General error: {error}")
        return jsonify({"status": "Error", "message": "General error: " + str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)