"""The Endpoints to manage the WORKERS"""
import json
import uuid
from datetime import datetime, timedelta, timezone
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware
from flask import current_app as APP

WORKER_API = Blueprint('worker_api', __name__)

@WORKER_API.route('/workers', methods=['GET'])
@auth_middleware.auth.login_required
def get_workers():
    """Return all workers
    @return: 200: an array of all known WORKERS as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for worker_obj in session.query(db.Workers).all():
            is_online = False
            if worker_obj.heartbeat_date and worker_obj.heartbeat_date > (datetime.now(timezone.utc) - timedelta(minutes = 5)):
                is_online = True

            res.append({'id': worker_obj.id, 'name': worker_obj.name, 'heartbeat_date': worker_obj.heartbeat_date, 'is_online': is_online, 'timestamp': worker_obj.timestamp})
        return jsonify(res)


@WORKER_API.route('/workers/', defaults={'_id': None}, methods=['GET'])
@WORKER_API.route('/workers/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_worker_by_id(_id):
    """Get worker details by it's id
    @param _id: the id
    @return: 200: a WORKERS as a flask/response object \
    with application/json mimetype.
    @raise 404: if worker not found
    """

    with db.SessionLocal.begin() as session:
        worker_obj = None
        if _id:
            worker_obj = session.query(db.Workers).where(db.Workers.id == _id).first()
        # if no ID is supplied, try to take the worker api token match
        elif 'worker_id' in APP.config:
            worker_obj = session.query(db.Workers).where(db.Workers.id == APP.config['worker_id']).first()
        
        is_online = False
        if worker_obj.heartbeat_date and worker_obj.heartbeat_date > (datetime.now(timezone.utc) - timedelta(minutes = 5)):
            is_online = True

        if worker_obj is not None:
            return jsonify({'id': worker_obj.id, 'name': worker_obj.name, 'token': worker_obj.token, 'heartbeat_date': worker_obj.heartbeat_date, 'is_online': is_online, 'timestamp': worker_obj.timestamp})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@WORKER_API.route('/workers/heartbeat/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def send_worker_heartbeat_by_id(_id):
    """ Sends a new heartbeat for a worker
    @param _id: the id
    @return: 200: a WORKERS as a flask/response object \
    with application/json mimetype.
    @raise 404: if worker not found
    """

    with db.SessionLocal.begin() as session:
        worker_obj = session.query(db.Workers).where(db.Workers.id == _id).first()
        if not worker_obj:
            abort(404)

        worker_obj.heartbeat_date = datetime.now()
        return jsonify({"id": _id}), 200


@WORKER_API.route('/workers', methods=['POST'])
@auth_middleware.auth.login_required
def create_worker():
    """Create a worker
    @param name: post : the name of the worker generator
    @return: 201: a new_uuid as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood worker
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Workers.id).where(db.Workers.name == data.get('name')).count() != 0:
            return jsonify({'error': 'name is already registered'}), 400

        token = str(uuid.uuid4())

        worker_obj = db.Workers(name=data.get('name'), token=token, timestamp=datetime.now())
        session.add(worker_obj)
        session.flush()
        return jsonify({"id": worker_obj.id, "token": token}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)


@WORKER_API.route('/workers/<int:_id>', methods=['PUT'])
@auth_middleware.auth.login_required
def edit_worker(_id):
    """Edit a worker
    @param name: post : the name of the worker
    @param generator: post : the generator code of the worker
    @return: 200: a worker as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood worker
    """

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Workers).where(db.Workers.id == _id).count() == 0:
            return jsonify({'error': 'worker obj with id is not found'}), 404

        if session.query(db.Workers.id).where(db.Workers.name == data.get('name'), db.Workers.id != _id).first() is not None:
            return jsonify({'error': 'name is already registered'}), 400 # existing user

        worker_obj = session.query(db.Workers).where(db.Workers.id == _id).first()
        worker_obj.name = data.get('name')
        session.flush()
        return jsonify({"id": worker_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)


@WORKER_API.route('/workers/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_worker(_id):
    """Delete a worker
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if worker not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Workers).where(db.Workers.id == _id).count() != 0:
            session.query(db.Workers).where(db.Workers.id == _id).delete()
            return '', 204

    return jsonify({'error': 'worker obj with id is not found'}), 404