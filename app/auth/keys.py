from flask import request, jsonify, g
from uuid import uuid4

from .. import db
from ..models import ApiKey, User
from . import auth_bp
from ..pipelines import login_required, super_admin_required


@auth_bp.route('/api-keys', methods=['POST'])
@login_required
def create_api_key():
    data = request.get_json() or {}
    scopes = data.get('scopes', [])
    if not isinstance(scopes, list):
        return jsonify({'error': 'scopes must be a list'}), 400

    target_user = g.current_user
    target_user_id = data.get('user_id')
    if target_user_id:
        if target_user.role != 'super_admin':
            return jsonify({'error': 'Forbidden'}), 403
        target_user = User.query.get_or_404(target_user_id)

    token = uuid4().hex
    api_key = ApiKey(key=token, user=target_user, scopes=','.join(scopes))
    db.session.add(api_key)
    db.session.commit()
    return jsonify({'token': token, 'user_id': target_user.user_id, 'scopes': scopes}), 201


@auth_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def revoke_api_key(key_id):
    api_key = ApiKey.query.get_or_404(key_id)
    user = g.current_user
    if user.role != 'super_admin' and api_key.user_id != user.user_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(api_key)
    db.session.commit()
    return '', 204
