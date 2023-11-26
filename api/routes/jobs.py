"""The Endpoints to manage the STUDIES"""
import uuid
from datetime import datetime, timedelta, timezone
from flask import jsonify, abort, request, Blueprint
import json
from cron_converter import Cron
from flask import current_app as APP

import db
import auth_middleware

JOB_API = Blueprint('job_api', __name__)

@JOB_API.route('/jobs/next', methods=['GET'])
@auth_middleware.auth.login_required
def get_next_job():
    """Get the next job to perform (this function should only be executed by a worker, since it needs to have a worker_id set)
    @return: 200: a STUDY as a flask/response object \
    with application/json mimetype.
    @raise 404: if study not found
    """

    with db.SessionLocal.begin() as session:
        study_obj = session.query(db.Studys).where(
                db.and_(
                    db.and_(
                        db.or_( # condition to find jobs with old heartbeat
                            db.Studys.heartbeat_date == None,
                            db.Studys.heartbeat_date <= (datetime.now() - timedelta(minutes = 1))
                        ),
                        db.or_(
                            db.Studys.next_scan_date <= datetime.now(timezone.utc), # this condition for starting a planned new job
                            db.or_( # this condition in case a job was not complete and worker died
                                db.Studys.complete_date == None,
                                db.Studys.complete_date <= db.Studys.scan_date
                            ),
                        ),
                    ),
                    db.or_( # in case a specific worker was assigned to a study
                        db.Studys.worker_id == None,
                        db.Studys.worker_id == APP.config['worker_id']
                    )
                )
            ).order_by(db.asc(db.Studys.next_scan_date)).first()

        if study_obj:
            study_obj.heartbeat_date = datetime.now()
            study_obj.scan_date = datetime.now()

            # compute next execution time
            cron_instance = Cron()
            cron_instance.from_string(study_obj.cron_schedule)
            reference = datetime.now(timezone.utc)
            schedule = cron_instance.schedule(reference)
            study_obj.next_scan_date = schedule.next()

            return jsonify({'id': study_obj.id})

    # if nothing was found and thus not returned, make an 404
    abort(404)


@JOB_API.route('/jobs/heartbeat/<int:_id>', methods=['GET'])
@auth_middleware.auth.login_required
def register_heartbeat(_id):
    """ Sends a new heartbeat for a study
    @return: 200: as a flask/response object \
    with application/json mimetype.
    @raise 400: misunderstood study
    """

    with db.SessionLocal.begin() as session:
        study_obj = session.query(db.Studys).where(db.Studys.id == _id).first()
        if not study_obj:
            abort(404)

        study_obj.heartbeat_date = datetime.now()
        return jsonify({"id": _id}), 200

    # if nothing was stored and thus not returned, make an 400
    abort(400)