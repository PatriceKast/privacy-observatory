"""The Endpoints to manage the DOMAINS"""
import json
from datetime import datetime
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware
from flask import current_app as APP

USER_API = Blueprint('user_api', __name__)

@USER_API.route('/users', methods=['GET'])
@auth_middleware.auth.login_required
def get_users():
    """Return all users
    @return: 200: an array of all known USERS as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for user_obj in session.query(db.Users).all():
            res.append({'id': user_obj.id, 'name': user_obj.name, 'email': user_obj.email, 'timestamp': user_obj.timestamp})
        return jsonify(res)

@USER_API.route('/users', methods = ['POST'])
@auth_middleware.auth.login_required
def new_user():
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if name is None or email is None or password is None:
        return jsonify({'error': 'a name, an email as well as a password must be sent'}), 400 # missing arguments

    with db.SessionLocal.begin() as session:
        if session.query(db.Users.id).where(db.Users.name == name).first() is not None:
            return jsonify({'error': 'name is already registered'}), 400 # existing user

        user_obj = db.Users(name = name, email = email, timestamp=datetime.now())
        user_obj.hash_password(password)
        session.add(user_obj)
        session.flush()

        return jsonify({"id": user_obj.id}), 201

@USER_API.route('/users/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_user_by_id(_id):
    """Return a user
    @return: 200: a USERS as a flask/response object \
    flask/response object with application/json mimetype.
    """

    with db.SessionLocal.begin() as session:
        user_obj = session.query(db.Users).where(db.Users.id == _id).first()

        return jsonify({'id': user_obj.id, 'name': user_obj.name, 'email': user_obj.email, 'timestamp': user_obj.timestamp})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@USER_API.route('/users/<int:_id>', methods=['PUT'])
@auth_middleware.auth.login_required
def edit_user(_id):
    """Edit a user
    @param name: post : the name of the user
    @param email: post : the email code of the user
    @return: 200: a user as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood user
    """

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)
    if not data.get('email'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Users.id).where(db.Users.id == _id).count() == 0:
            return jsonify({'error': 'user obj with id is not found'}), 404

        if session.query(db.Users.id).where(db.Users.name == data.get('name'), db.Users.id != _id).first() is not None:
            return jsonify({'error': 'name is already registered'}), 400 # existing user

        user_obj = session.query(db.Users).where(db.Users.id == _id).first()
        user_obj.name = data.get('name')
        user_obj.email = data.get('email')
        session.flush()
        return jsonify({"id": user_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)

@USER_API.route('/users/token', methods=['GET'])
@auth_middleware.auth.login_required
def get_auth_token():
    token = APP.config['user_jwt']

    with db.SessionLocal.begin() as session:
        user_obj = session.query(db.Users).where(
                db.or_(
                    db.Users.id == APP.config['user_id']
                )
            ).first()

        return jsonify({ 'id': user_obj.id, 'name': user_obj.name, 'email': user_obj.email, 'token': token.decode('ascii') })

@USER_API.route('/users/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_users(_id):
    """Delete a user
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if user not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Users).where(db.Users.id == _id).count() != 0:
            session.query(db.Users).where(db.Users.id == _id).delete()
            return '', 204

    return jsonify({'error': 'user obj with id is not found'}), 404