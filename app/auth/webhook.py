from flask import request, jsonify
from uuid import uuid4

from .. import db
from ..models import Account, User, ApiKey
from . import auth_bp


@auth_bp.route('/auth/webhook', methods=['GET'])
def auth_webhook():
    # When Chatwoot triggers this webhook it now sends the data as query
    # parameters in a GET request.  Parse the arguments accordingly.
    data = request.args.to_dict()
    required_fields = ['account_id', 'user_id', 'user_email', 'user_name']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {", ".join(missing)}'}), 400

    account_id = data['account_id']
    user_id = data['user_id']
    user_email = data['user_email']
    user_name = data['user_name']

    # Get or create account
    account = Account.query.get(account_id)
    if account is None:
        account = Account(id=account_id, name=f'Account {account_id}')
        db.session.add(account)

    # Validate user
    user = User.query.get(user_id)
    if user:
        if (user.user_email != user_email or
                user.user_name != user_name or
                user.account_id != account_id):
            return jsonify({'error': 'user_id conflict with existing user'}), 400
    else:
        user = User(user_id=user_id, user_email=user_email,
                    user_name=user_name, account=account)
        db.session.add(user)

    # Generate token
    token = uuid4().hex
    api_key = ApiKey(key=token, user=user)
    db.session.add(api_key)
    db.session.commit()

    return jsonify({'token': token})
