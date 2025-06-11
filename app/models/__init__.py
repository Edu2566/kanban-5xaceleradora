from .. import db
from datetime import datetime

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    users = db.relationship('User', back_populates='account', cascade='all, delete-orphan')
    pipelines = db.relationship('Pipeline', back_populates='account', cascade='all, delete-orphan')


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    account = db.relationship('Account', back_populates='users')
    pipelines = db.relationship('Pipeline', secondary='pipeline_users', back_populates='users')
    stages = db.relationship('Stage', secondary='stage_users', back_populates='users')
    api_keys = db.relationship('ApiKey', back_populates='user', cascade='all, delete-orphan')


pipeline_users = db.Table(
    'pipeline_users',
    db.Column('pipeline_id', db.Integer, db.ForeignKey('pipelines.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
)

stage_users = db.Table(
    'stage_users',
    db.Column('stage_id', db.Integer, db.ForeignKey('stages.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
)


class Pipeline(db.Model):
    __tablename__ = 'pipelines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

    account = db.relationship('Account', back_populates='pipelines')
    stages = db.relationship('Stage', back_populates='pipeline', cascade='all, delete-orphan')
    users = db.relationship('User', secondary='pipeline_users', back_populates='pipelines')


class Stage(db.Model):
    __tablename__ = 'stages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer)
    pipeline_id = db.Column(db.Integer, db.ForeignKey('pipelines.id'))

    pipeline = db.relationship('Pipeline', back_populates='stages')
    users = db.relationship('User', secondary='stage_users', back_populates='stages')
    negotiations = db.relationship('Negotiation', back_populates='stage', cascade='all, delete-orphan')


class Negotiation(db.Model):
    __tablename__ = 'negotiations'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer)
    stage_id = db.Column(db.Integer, db.ForeignKey('stages.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    value = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    stage = db.relationship('Stage', back_populates='negotiations')
    owner = db.relationship('User')


class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='api_keys')
