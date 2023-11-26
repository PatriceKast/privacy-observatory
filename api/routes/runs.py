"""The Endpoints to manage the STUDIES"""
import uuid
from datetime import datetime, timedelta, timezone
from flask import jsonify, abort, request, Blueprint
import json

import db
import auth_middleware

RUN_API = Blueprint('run_api', __name__)

@RUN_API.route('/runs', methods=['GET'])
@auth_middleware.auth.login_required
def get_runs():
    """Return all runs
    @return: 200: an array of all known STUDIES as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for run_obj in session.query(db.Runs.id, db.Runs.study_id, db.Runs.duration, db.Runs.timestamp).all():
            res.append({'id': run_obj.id, 'study_id': run_obj.study_id, 'duration': str(run_obj.duration), 'timestamp': run_obj.timestamp})
        return jsonify(res)


@RUN_API.route('/runs/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_run_by_id(_id):
    """Get run details by it's id
    @param _id: the id
    @return: 200: a STUDIES as a flask/response object \
    with application/json mimetype.
    @raise 404: if study not found
    """

    with db.SessionLocal.begin() as session:
        run_obj = session.query(db.Runs).where(db.Runs.id == _id).first()
        if not run_obj:
            abort(404)

        measurements = []
        for measurement_obj in session.query(db.Measurements.id, db.Measurements.key, db.Measurements.value).where(db.Measurements.domain_id == None, db.Measurements.run_id == _id).all():
            measurements.append({
                'id': measurement_obj.id,
                'domain': None,
                'key': measurement_obj.key,
                'value': measurement_obj.value
            })

        for measurement_obj in session.query(db.Measurements.id, db.Measurements.key, db.Measurements.value, db.Domains.name).where(db.Measurements.domain_id == db.Domains.id, db.Measurements.run_id == _id).all():
            measurements.append({
                'id': measurement_obj.id,
                'domain': measurement_obj.name,
                'key': measurement_obj.key,
                'value': measurement_obj.value
            })

        return jsonify({'id': run_obj.id, 'study_id': run_obj.study_id, 'output': run_obj.output, 'duration': str(run_obj.duration), 'measurements': measurements, 'timestamp': run_obj.timestamp,
            'num_unique_run_measurements': session.query(db.Measurements).where(db.Measurements.run_id == _id).count()})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@RUN_API.route('/runs', methods=['POST'])
@auth_middleware.auth.login_required
def store_new_run():
    """Stores a new run of a study (passed is the study_id)
    @return: 200: a new_uuid as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood study
    """

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    with db.SessionLocal.begin() as session:
        study_obj = session.query(db.Studys).where(db.Studys.id == int(data['study_id'])).first()
        if not study_obj:
            return jsonify({'error': 'the referenced job was not found'}), 404

        measurement_timestamp = datetime.now()
        duration_interval = timedelta(minutes = 0)

        # and old measurement is registered
        if data.get('timestamp'):
            measurement_timestamp = data.get('timestamp')
        
        # otherwise, a worker is uploading some data
        else:
            study_obj.complete_date = datetime.now()
            if study_obj.scan_date is None:
                study_obj.scan_date = datetime.now()
            
            duration_interval = (datetime.now(timezone.utc) - study_obj.scan_date)

        run_obj = db.Runs(study_id=study_obj.id, output=data['output'], duration=duration_interval, timestamp=measurement_timestamp)
        session.add(run_obj)
        session.flush()

        for key in data.get('stats').keys():
            measurement_obj = db.Measurements(key=key, value=json.dumps(data.get('stats')[key]), run_id=run_obj.id, domain_id=None, timestamp=measurement_timestamp)
            session.add(measurement_obj)
        
        if data.get('doms'):
            for dom in data.get('doms').keys():
                dom_search = dom
                # remove www subdomain if domain has one
                if dom_search.startswith("www."):
                    dom_search = dom[4:]

                domain_obj = session.query(db.Domains).where(db.Domains.name == dom_search).first()
                if not domain_obj:
                    domain_obj = db.Domains(name=dom_search, timestamp=measurement_timestamp)
                    session.add(domain_obj)
                    session.flush()

                for key in data.get('doms')[dom]:
                    measurement_obj = db.Measurements(key=key, value=json.dumps(data.get('doms')[dom][key]), run_id=run_obj.id, domain_id=domain_obj.id, timestamp=measurement_timestamp)
                    session.add(measurement_obj)


        return jsonify({"id": run_obj.id}), 200

    # if nothing was stored and thus not returned, make an 400
    abort(400)