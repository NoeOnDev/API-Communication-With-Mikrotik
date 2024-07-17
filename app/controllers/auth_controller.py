# app/controllers/auth_controller.py
from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    result = AuthService.connect(data)
    return jsonify(result)
