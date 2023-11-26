"""The Endpoints to manage the MEASUREMENTS"""
import uuid
from datetime import datetime, timedelta
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware

MEASUREMENT_API = Blueprint('measurement_api', __name__)

@MEASUREMENT_API.route('/measurements', methods=['GET'])
@auth_middleware.auth.login_required
def get_measurements():
    """Return all measurements
    @return: 200: an array of all known MEASUREMENTS as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for measurement_obj in session.query(db.Measurements).all():
            res.append({'id': measurement_obj.id, 'key': measurement_obj.key, 'value': measurement_obj.value, 'run_id': measurement_obj.run_id, 'run_id': measurement_obj.run_id, 'domain_id': measurement_obj.domain_id, 'timestamp': measurement_obj.timestamp})
        return jsonify(res)


@MEASUREMENT_API.route('/measurements/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_measurement_by_id(_id):
    """Get measurement details by it's id
    @param _id: the id
    @return: 200: a MEASUREMENTS as a flask/response object \
    with application/json mimetype.
    @raise 404: if measurement not found
    """

    with db.SessionLocal.begin() as session:
        measurement_obj = session.query(db.Measurements).where(db.Measurements.id == _id).first()
        return jsonify({'id': measurement_obj.id, 'key': measurement_obj.key, 'value': measurement_obj.value, 'run_id': measurement_obj.run_id, 'run_id': measurement_obj.run_id, 'domain_id': measurement_obj.domain_id, 'timestamp': measurement_obj.timestamp})

    # if nothing was found and thus not returned, make an 404
    abort(404)
    

@MEASUREMENT_API.route('/measurements/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_measurement(_id):
    """Delete a measurement
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if measurement not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Measurements).where(db.Measurements.id == _id).count() != 0:
            session.query(db.Measurements).where(db.Measurements.id == _id).delete()
            return '', 204

    return jsonify({'error': 'measurement obj with id is not found'}), 404