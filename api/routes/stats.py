"""The Endpoints to manage the STATS"""
import json
from datetime import datetime, timedelta, timezone
from flask import jsonify, abort, request, Blueprint

import db
import auth_middleware

STATS_API = Blueprint('stats_api', __name__)

@STATS_API.route('/stats', methods=['GET'])
@auth_middleware.auth.login_required
def get_stats():
    """Return all important stats
    @return: 200: an dict of useful STATS
    """
    with db.SessionLocal.begin() as session:
        domains = {
            'measurements_per_month': {}
        }
        for join_obj in session.query(db.func.count(db.Measurements.id).label('count'), db.func.min(db.Measurements.timestamp).label('timestamp')).group_by( db.extract('year', db.Measurements.timestamp), db.extract('month', db.Measurements.timestamp)).all():
            domains['measurements_per_month'][str(join_obj.timestamp)] = join_obj.count

        objs = {
            'num_studies': session.query(db.Studys).count(),
            'num_domains': session.query(db.Domains).count(),
            'num_measurements': session.query(db.Measurements).count(),
            'num_workers_online': session.query(db.Workers).where(db.Workers.heartbeat_date > (datetime.now() - timedelta(minutes = 5))).count(),
            'measurements': domains,
            'about': 'The Privacy Observatory Platform enables long-term periodic studies of the internet.',
            'created_by': 'Prof. Dr. David Basin, Ahmed Bouhoula, Karel Kubicek, Patrice Kast',
        }
        return jsonify(objs)