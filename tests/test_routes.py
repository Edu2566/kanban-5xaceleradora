import pytest
from app import create_app, db
from app.models import Account, User, ApiKey, Pipeline

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def get_token(client):
    payload = {
        'account_id': 1,
        'user_id': 1,
        'user_email': 'test@example.com',
        'user_name': 'Tester'
    }
    response = client.get('/auth/webhook', query_string=payload)
    assert response.status_code == 200
    token = response.get_json()['token']
    # Promote user to supervisor
    user = User.query.get(1)
    user.role = 'supervisor'
    db.session.commit()
    return token

def test_auth_webhook_creates_user(client):
    payload = {
        'account_id': 1,
        'user_id': 2,
        'user_email': 'new@example.com',
        'user_name': 'New User'
    }
    response = client.get('/auth/webhook', query_string=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert User.query.get(2) is not None
    assert Account.query.get(1) is not None

def test_create_and_list_pipelines(client):
    token = get_token(client)
    headers = {'X-API-Key': token}
    create_resp = client.post('/pipelines', json={'name': 'Sales'}, headers=headers)
    assert create_resp.status_code == 201
    pipeline_id = create_resp.get_json()['id']
    list_resp = client.get('/pipelines', headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.get_json()
    assert any(p['id'] == pipeline_id for p in data)

def test_access_without_token_forbidden(client):
    resp = client.get('/pipelines')
    assert resp.status_code == 403
