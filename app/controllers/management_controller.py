from flask import Blueprint, request, jsonify
from ..services.management_service import ManagementService

management_bp = Blueprint('management_bp', __name__)

@management_bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    token = request.headers.get('Authorization')
    user_id = request.json.get('id')
    result = ManagementService.delete_user(token, user_id)
    return jsonify(result)

@management_bp.route('/add_user', methods=['POST'])
def add_user():
    token = request.headers.get('Authorization')
    user_data = request.get_json()
    result = ManagementService.add_user(token, user_data)
    return jsonify(result)
