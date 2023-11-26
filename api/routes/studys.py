"""The Endpoints to manage the STUDIES"""
import uuid
from datetime import datetime, timedelta, timezone
from flask import jsonify, abort, request, Blueprint
from cron_converter import Cron
import json

import db
import auth_middleware
from helper import is_json

STUDY_API = Blueprint('study_api', __name__)

@STUDY_API.route('/studys', methods=['GET'])
@auth_middleware.auth.login_required
def get_studys():
    """Return all studys
    @return: 200: an array of all known STUDIES as a \
    flask/response object with application/json mimetype.
    """
    with db.SessionLocal.begin() as session:
        res = []
        for study_obj in session.query(db.Studys).all():
            is_executing = False
            if study_obj.heartbeat_date and study_obj.heartbeat_date > (datetime.now(timezone.utc) - timedelta(minutes = 5)):
                is_executing = True

            res.append({'id': study_obj.id, 'name': study_obj.name, 'author': study_obj.author, 'composefile': study_obj.composefile, 'is_executing': is_executing, 'output_format': study_obj.output_format, 'domainset_id': study_obj.domainset_id, 'worker_id': study_obj.worker_id,
                'cron_schedule': study_obj.cron_schedule, 'next_scan_date': study_obj.next_scan_date, 'scan_date': study_obj.scan_date, 'complete_date': study_obj.complete_date, 'heartbeat_date': study_obj.heartbeat_date, 'timestamp': study_obj.timestamp})
        return jsonify(res)
        

@STUDY_API.route('/studys/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def get_study_by_id(_id):
    """Get study details by it's id
    @param _id: the id
    @return: 200: a STUDIES as a flask/response object \
    with application/json mimetype.
    @raise 404: if study not found
    """

    with db.SessionLocal.begin() as session:
        study_obj = session.query(db.Studys).where(db.Studys.id == _id).first()

        runs = []
        for run_obj in session.query(db.Runs.id, db.Runs.duration, db.Runs.timestamp).where(db.Runs.study_id == _id).all():
            runs.append({'id': run_obj.id, 'duration': str(run_obj.duration), 'timestamp': run_obj.timestamp})


        measurements = {}
        for measurement_obj in session.query(db.Measurements.key, db.Measurements.value, db.Measurements.timestamp).where(db.Runs.study_id == _id, db.Measurements.run_id == db.Runs.id, db.Measurements.domain_id == None).all():
            if measurement_obj.key not in measurements.keys():
                measurements[measurement_obj.key] = {}
            
            if is_json(measurement_obj.value):
                measurements[measurement_obj.key][str(measurement_obj.timestamp)] = json.loads(measurement_obj.value)
            else:
                measurements[measurement_obj.key][str(measurement_obj.timestamp)] = measurement_obj.value
        

        return jsonify({'id': study_obj.id, 'name': study_obj.name, 'author': study_obj.author, 'composefile': study_obj.composefile, 'output_format': study_obj.output_format, 'domainset_id': study_obj.domainset_id, 'worker_id': study_obj.worker_id,
            'cron_schedule': study_obj.cron_schedule, 'measurements': measurements, 'runs': runs, 'next_scan_date': study_obj.next_scan_date, 'scan_date': study_obj.scan_date, 'complete_date': study_obj.complete_date,
            'heartbeat_date': study_obj.heartbeat_date, 'timestamp': study_obj.timestamp,
            'num_unique_study_runs': session.query(db.Runs).where(db.Runs.study_id == _id).count(), 'num_unique_study_measurements': session.query(db.Measurements, db.Runs).where(db.Measurements.run_id == db.Runs.id, db.Runs.study_id == _id).count()
            })

    # if nothing was found and thus not returned, make an 404
    abort(404)


@STUDY_API.route('/studys', methods=['POST'])
@auth_middleware.auth.login_required
def create_study():
    """Create a study
    @param name: post : the name of the study generator
    @param generator: post : the generator code of the study
    @return: 201: a new_uuid as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood study
    """
    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)
    if not data.get('author'):
        abort(400)
    if not data.get('composefile'):
        abort(400)
    if not data.get('output_format'):
        abort(400)
    if not data.get('domainset_id'):
        abort(400)
    if not data.get('cron_schedule'):
        abort(400)
    
    worker_id = None
    if data.get('worker_id') and data.get('worker_id') != 'None':
        worker_id = data.get('worker_id')

    with db.SessionLocal.begin() as session:
        if session.query(db.Domainsets.id).where(db.Domainsets.id == data.get('domainset_id')).count() == 0:
            return jsonify({'error': 'domainset obj with id is not found'}), 400

        if session.query(db.Studys.id).where(db.Studys.name == data.get('name')).count() != 0:
            return jsonify({'error': 'study name is already registered'}), 400

        # compute next execution time
        cron_instance = Cron()
        cron_instance.from_string(data.get('cron_schedule'))
        reference = datetime.now()
        schedule = cron_instance.schedule(reference)
        next_scan_date = schedule.next()

        study_obj = db.Studys(name=data.get('name'), author=data.get('author'), composefile=data.get('composefile'), output_format=data.get('output_format'), domainset_id=data.get('domainset_id'), worker_id=worker_id,
            cron_schedule=data.get('cron_schedule'), next_scan_date=next_scan_date, timestamp=datetime.now())
        session.add(study_obj)
        session.flush()
        return jsonify({"id": study_obj.id}), 201


    # if nothing was stored and thus not returned, make an 400
    abort(400)


@STUDY_API.route('/studys/<int:_id>', methods=['PUT'])
@auth_middleware.auth.login_required
def edit_study(_id):
    """Edit a study
    @param name: post : the name of the study generator
    @param generator: post : the generator code of the study
    @return: 200: a study as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood study
    """

    if not request.get_json():
        abort(400)
    data = request.get_json(force=True)

    if not data.get('name'):
        abort(400)
    if not data.get('author'):
        abort(400)
    if not data.get('composefile'):
        abort(400)
    if not data.get('output_format'):
        abort(400)
    if not data.get('domainset_id'):
        abort(400)
    if not data.get('cron_schedule'):
        abort(400)
    
    worker_id = None
    if data.get('worker_id') and data.get('worker_id') != 'None':
        worker_id = data.get('worker_id')

    with db.SessionLocal.begin() as session:
        if session.query(db.Domainsets.id).where(db.Domainsets.id == data.get('domainset_id')).count() == 0:
            return jsonify({'error': 'domainset obj with id is not found'}), 400

        if session.query(db.Studys.id).where(db.Studys.id == _id).count() == 0:
            return jsonify({'error': 'study obj with id is not found'}), 404

        if session.query(db.Studys.id).where(db.Studys.name == data.get('name'), db.Studys.id != _id).count() != 0:
            return jsonify({'error': 'name is already registered'}), 400

        # compute next execution time
        cron_instance = Cron()
        cron_instance.from_string(data.get('cron_schedule'))
        reference = datetime.now()
        schedule = cron_instance.schedule(reference)
        next_scan_date = schedule.next()

        study_obj = session.query(db.Studys).where(db.Studys.id == _id).first()
        study_obj.name = data.get('name')
        study_obj.author = data.get('author')
        study_obj.composefile = data.get('composefile')
        study_obj.output_format = data.get('output_format')
        study_obj.domainset_id = data.get('domainset_id')
        study_obj.worker_id = worker_id
        study_obj.cron_schedule = data.get('cron_schedule')
        study_obj.next_scan_date = next_scan_date
        session.flush()
        return jsonify({"id": study_obj.id}), 201

    # if nothing was stored and thus not returned, make an 400
    abort(400)

@STUDY_API.route('/studys/<int:_id>', methods=['DELETE'])
@auth_middleware.auth.login_required
def delete_study(_id):
    """Delete a study
    @param id: the id
    @return: 204: an empty payload.
    @raise 404: if study not found
    """

    with db.SessionLocal.begin() as session:
        if session.query(db.Studys).where(db.Studys.id == _id).count() != 0:
            session.query(db.Studys).where(db.Studys.id == _id).delete()
            return '', 204

    return jsonify({'error': 'study obj with id is not found'}), 404