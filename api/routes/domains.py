"""The Endpoints to manage the DOMAINS"""
import json
from datetime import datetime
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware

DOMAIN_API = Blueprint('domain_api', __name__)

@DOMAIN_API.route('/domains', methods=['GET'])
@auth_middleware.auth.login_required
def get_domains():
    """Return all domains, can use a filter GET query param for filter by entity name
    @return: 200: an array of all known DOMAINS as a \
    flask/response object with application/json mimetype.
    """
    filtr = None
    if request.args.get('filter') and request.args.get('filter') != "":
        filtr = request.args.get('filter')

    with db.SessionLocal.begin() as session:
        db_loop = None
        if filtr:
            db_loop = session.query(db.Domains.id, db.Domains.name, db.Domains.timestamp).filter(db.Domains.name.like("%" + filtr + "%")).limit(1000).all()
        else:
            db_loop = session.query(db.Domains.id, db.Domains.name, db.Domains.timestamp).limit(1000).all()

        res = []
        for domain_obj in db_loop:
            res.append({'id': domain_obj.id, 'name': domain_obj.name, 'timestamp': domain_obj.timestamp})
        return jsonify(res)

@DOMAIN_API.route('/domains/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_domain_by_id(_id):
    """Get domain details by it's id
    @param _id: the id
    @return: 200: a DOMAINS as a flask/response object \
    with application/json mimetype.
    @raise 404: if domain not found
    """

    with db.SessionLocal.begin() as session:
        domain_obj = session.query(db.Domains).where(db.Domains.id == _id).first()

        measurements = {}
        runs_collected = []
        runs = []
        for join_obj in session.query(db.Studys.name, db.Runs.id, db.Runs.duration, db.Runs.id, db.Runs.timestamp.label("run_timestamp"), db.Measurements.timestamp.label("measurement_timestamp"), db.Measurements.key, db.Measurements.value).where(db.Measurements.domain_id == _id, db.Runs.id == db.Measurements.run_id, db.Studys.id == db.Runs.study_id).all():
            key = join_obj.name + '.' + join_obj.key
            key = key.replace(' ', '_')
            if key not in measurements.keys():
                measurements[key] = {}
            
            measurements[key][str(join_obj.measurement_timestamp)] = join_obj.value

            if join_obj.id not in runs_collected:
                runs.append({'id': join_obj.id, 'study': join_obj.name, 'duration': str(join_obj.duration), 'timestamp': join_obj.run_timestamp})
                runs_collected.append(join_obj.id)

        return jsonify({'id': domain_obj.id, 'name': domain_obj.name, 'measurements': measurements, 'runs': runs, 'timestamp': domain_obj.timestamp})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@DOMAIN_API.route('/domains', methods=['POST'])
@auth_middleware.auth.login_required
def create_domain():
    """Create a domain
    @param domain: post : the domain of the domain generator
    @param generator: post : the generator code of the domain
    @return: 201: a id as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood domain
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)

    with db.SessionLocal.begin() as session:
        if session.query(db.Domains).where(db.Domains.name == data.get('name')).count() != 0:
            return jsonify({'error': 'domain is already registered'}), 400

        domain_obj = db.Domains(name=data.get('name'), timestamp=datetime.now())
        session.add(domain_obj)
        session.flush()
        return jsonify({"id": domain_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)


@DOMAIN_API.route('/domains/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_domain(_id):
    """Delete a domain
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if domain not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Domains).where(db.Domains.id == _id).count() != 0:
            session.query(db.Domains).where(db.Domains.id == _id).delete()
            return '', 204

    return jsonify({'error': 'domain obj with id is not found'}), 404