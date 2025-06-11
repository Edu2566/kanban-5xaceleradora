from flask import Blueprint, request, jsonify, g

from . import db
from .models import User
from .pipelines import super_admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users', methods=['GET'])
@super_admin_required
def list_users():
    users = User.query.all()
    return jsonify([
        {
            'user_id': u.user_id,
            'role': u.role,
            'account_id': u.account_id,
        } for u in users
    ])


@admin_bp.route('/admin/users/<int:user_id>/role', methods=['PUT'])
@super_admin_required
def update_user_role(user_id):
    data = request.get_json() or {}
    role = data.get('role')
    if not role:
        return jsonify({'error': 'Missing role'}), 400
    user = User.query.get_or_404(user_id)
    user.role = role
    db.session.commit()
    return jsonify({'user_id': user.user_id, 'role': user.role, 'account_id': user.account_id})
