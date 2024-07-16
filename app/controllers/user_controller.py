# app/controllers/user_controller.py
from flask import Blueprint, request, jsonify
from ..services.user_service import UserService

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['POST'])
def get_users():
    token = request.headers.get('Authorization')
    result = UserService.get_users(token)
    return jsonify(result)