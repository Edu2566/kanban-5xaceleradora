from flask import Blueprint, request, jsonify, g
from functools import wraps

from .. import db
from ..models import Pipeline, Stage, ApiKey

pipelines_bp = Blueprint('pipelines', __name__)


def get_current_user():
    token = request.headers.get('X-API-Key')
    if not token:
        return None
    api_key = ApiKey.query.filter_by(key=token).first()
    return api_key.user if api_key else None


def supervisor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'supervisor':
            return jsonify({'error': 'Forbidden'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper


def pipeline_access_required(f):
    @wraps(f)
    def wrapper(pipeline_id, *args, **kwargs):
        pipeline = Pipeline.query.get_or_404(pipeline_id)
        user = g.current_user
        if pipeline.account_id != user.account_id and user not in pipeline.users:
            return jsonify({'error': 'Forbidden'}), 403
        g.pipeline = pipeline
        return f(pipeline_id, *args, **kwargs)
    return wrapper


@pipelines_bp.route('/pipelines', methods=['POST'])
@supervisor_required
def create_pipeline():
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Missing name'}), 400
    user = g.current_user
    max_pos = db.session.query(db.func.max(Pipeline.position)).filter_by(account_id=user.account_id).scalar() or 0
    pipeline = Pipeline(name=name, account_id=user.account_id, position=max_pos + 1)
    db.session.add(pipeline)
    pipeline.users.append(user)
    db.session.commit()
    return jsonify({'id': pipeline.id, 'name': pipeline.name}), 201


@pipelines_bp.route('/pipelines', methods=['GET'])
@supervisor_required
def list_pipelines():
    user = g.current_user
    pipelines = Pipeline.query.filter((Pipeline.account_id == user.account_id) | (Pipeline.users.contains(user))).order_by(Pipeline.position).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in pipelines])


@pipelines_bp.route('/pipelines/<int:pipeline_id>', methods=['GET'])
@supervisor_required
@pipeline_access_required
def get_pipeline(pipeline_id):
    pipeline = g.pipeline
    return jsonify({'id': pipeline.id, 'name': pipeline.name})


@pipelines_bp.route('/pipelines/<int:pipeline_id>', methods=['PUT'])
@supervisor_required
@pipeline_access_required
def update_pipeline(pipeline_id):
    data = request.get_json() or {}
    name = data.get('name')
    if name:
        g.pipeline.name = name
    db.session.commit()
    return jsonify({'id': g.pipeline.id, 'name': g.pipeline.name})


@pipelines_bp.route('/pipelines/<int:pipeline_id>', methods=['DELETE'])
@supervisor_required
@pipeline_access_required
def delete_pipeline(pipeline_id):
    db.session.delete(g.pipeline)
    db.session.commit()
    return '', 204


@pipelines_bp.route('/pipelines/reorder', methods=['POST'])
@supervisor_required
def reorder_pipelines():
    data = request.get_json() or {}
    ids = data.get('pipeline_ids')
    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'pipeline_ids must be a list'}), 400
    user = g.current_user
    pipelines = Pipeline.query.filter(Pipeline.id.in_(ids)).all()
    if any(p.account_id != user.account_id and user not in p.users for p in pipelines):
        return jsonify({'error': 'Forbidden'}), 403
    for position, pid in enumerate(ids, start=1):
        Pipeline.query.filter_by(id=pid).update({'position': position})
    db.session.commit()
    return '', 204


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages', methods=['POST'])
@supervisor_required
@pipeline_access_required
def create_stage(pipeline_id):
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Missing name'}), 400
    max_pos = db.session.query(db.func.max(Stage.position)).filter_by(pipeline_id=pipeline_id).scalar() or 0
    stage = Stage(name=name, pipeline_id=pipeline_id, position=max_pos + 1)
    db.session.add(stage)
    stage.users.append(g.current_user)
    db.session.commit()
    return jsonify({'id': stage.id, 'name': stage.name}), 201


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages', methods=['GET'])
@supervisor_required
@pipeline_access_required
def list_stages(pipeline_id):
    stages = Stage.query.filter_by(pipeline_id=pipeline_id).order_by(Stage.position).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in stages])


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages/<int:stage_id>', methods=['GET'])
@supervisor_required
@pipeline_access_required
def get_stage(pipeline_id, stage_id):
    stage = Stage.query.get_or_404(stage_id)
    if stage.pipeline_id != pipeline_id:
        return jsonify({'error': 'Invalid stage'}), 400
    return jsonify({'id': stage.id, 'name': stage.name})


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages/<int:stage_id>', methods=['PUT'])
@supervisor_required
@pipeline_access_required
def update_stage(pipeline_id, stage_id):
    stage = Stage.query.get_or_404(stage_id)
    if stage.pipeline_id != pipeline_id:
        return jsonify({'error': 'Invalid stage'}), 400
    data = request.get_json() or {}
    name = data.get('name')
    if name:
        stage.name = name
    db.session.commit()
    return jsonify({'id': stage.id, 'name': stage.name})


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages/<int:stage_id>', methods=['DELETE'])
@supervisor_required
@pipeline_access_required
def delete_stage(pipeline_id, stage_id):
    stage = Stage.query.get_or_404(stage_id)
    if stage.pipeline_id != pipeline_id:
        return jsonify({'error': 'Invalid stage'}), 400
    db.session.delete(stage)
    db.session.commit()
    return '', 204


@pipelines_bp.route('/pipelines/<int:pipeline_id>/stages/reorder', methods=['POST'])
@supervisor_required
@pipeline_access_required
def reorder_stages(pipeline_id):
    data = request.get_json() or {}
    ids = data.get('stage_ids')
    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'stage_ids must be a list'}), 400
    stages = Stage.query.filter(Stage.id.in_(ids), Stage.pipeline_id == pipeline_id).all()
    if len(stages) != len(ids):
        return jsonify({'error': 'Invalid stages'}), 400
    for position, sid in enumerate(ids, start=1):
        Stage.query.filter_by(id=sid).update({'position': position})
    db.session.commit()
    return '', 204