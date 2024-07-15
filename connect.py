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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)