"""The Endpoints to manage the DOMAINSETS"""
import json
from datetime import datetime, timedelta
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware

DOMAINSET_API = Blueprint('domainset_api', __name__)

@DOMAINSET_API.route('/domainsets', methods=['GET'])
@auth_middleware.auth.login_required
def get_domainsets():
    """Return all domainsets
    @return: 200: an array of all known DOMAINSETS as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for domainset_obj in session.query(db.Domainsets.id, db.Domainsets.name, db.Domainsets.timestamp).all():
            res.append({'id': domainset_obj.id, 'name': domainset_obj.name, 'timestamp': domainset_obj.timestamp})
        return jsonify(res)


@DOMAINSET_API.route('/domainsets/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_domainset_by_id(_id):
    """Get domainset details by it's id
    @param _id: the id
    @return: 200: a DOMAINSETS as a flask/response object \
    with application/json mimetype.
    @raise 404: if domainset not found
    """

    with db.SessionLocal.begin() as session:
        domainset_obj = session.query(db.Domainsets).where(db.Domainsets.id == _id).first()
        return jsonify({'id': domainset_obj.id, 'name': domainset_obj.name, 'generator': domainset_obj.generator, 'timestamp': domainset_obj.timestamp, 'num_linked_studies': session.query(db.Studys.id).where(db.Studys.domainset_id == _id).count()})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@DOMAINSET_API.route('/domainsets/run/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def run_domainset_by_id(_id):
    """Execute the domainset details by it's id
    @param _id: the id
    @return: 200: a DOMAINSETS as a flask/response object \
    with application/json mimetype.
    @raise 404: if domainset not found
    """

    with db.SessionLocal.begin() as session:
        domainset_obj = session.query(db.Domainsets).where(db.Domainsets.id == _id).first()
        return domainset_obj.generator
        output = eval(domainset_obj.generator)
        return output

    # if nothing was found and thus not returned, make an 404
    abort(404)


@DOMAINSET_API.route('/domainsets', methods=['POST'])
@auth_middleware.auth.login_required
def create_domainset():
    """Create a domainset
    @param name: post : the name of the domainset generator
    @param generator: post : the generator code of the domainset
    @return: 201: a new_uuid as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood domainset
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)
    if not data.get('generator'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Domainsets.id).where(db.Domainsets.name == data.get('name')).count() != 0:
            return jsonify({'error': 'name is already registered'}), 400

        domainset_obj = db.Domainsets(name=data.get('name'), generator=data.get('generator'), timestamp=datetime.now())
        session.add(domainset_obj)
        session.flush()
        return jsonify({"id": domainset_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)



@DOMAINSET_API.route('/domainsets/<int:_id>', methods=['PUT'])
@auth_middleware.auth.login_required
def edit_domainset(_id):
    """Edit a domainset
    @param name: post : the name of the domainset generator
    @param generator: post : the generator code of the domainset
    @return: 200: a domainset as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood domainset
    """

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)
    if not data.get('generator'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Domainsets.id).where(db.Domainsets.id == _id).count() == 0:
            return jsonify({'error': 'domainset obj with id is not found'}), 404

        if session.query(db.Domainsets.id).where(db.Domainsets.name == data.get('name'), db.Domainsets.id != _id).count() != 0:
            return jsonify({'error': 'name is already registered'}), 400

        domainset_obj = session.query(db.Domainsets).where(db.Domainsets.id == _id).first()
        domainset_obj.name = data.get('name')
        domainset_obj.generator = data.get('generator')
        session.flush()
        return jsonify({"id": domainset_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)



@DOMAINSET_API.route('/domainsets/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_domainset(_id):
    """Delete a domainset
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if domainset not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Domainsets.id).where(db.Domainsets.id == _id).count() != 0:
            session.query(db.Domainsets).where(db.Domainsets.id == _id).delete()
            return '', 204

    return jsonify({'error': 'domainset obj with id is not found'}), 404