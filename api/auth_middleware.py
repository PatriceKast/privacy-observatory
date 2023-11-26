from flask_httpauth import HTTPBasicAuth
from flask import current_app as APP

import db

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    with db.SessionLocal.begin() as session:
        # if a worker is requesting, allow
        # not used code: APP.config['worker_' + str(username_or_token)] = "not_set"
        worker_obj = session.query(db.Workers).where(db.Workers.token == username_or_token).first()
        if worker_obj:
            APP.config['worker_id'] = worker_obj.id
            return True

        user_obj = db.Users.verify_auth_token(session, username_or_token)
        if not user_obj:
            # in case there are no users registered, allow all
            if not session.query(db.Users).first():
                return True

            user_obj = session.query(db.Users).where(
                db.or_(
                    db.Users.name == username_or_token,
                    db.Users.email == username_or_token
                )
            ).first()
            if not user_obj or not user_obj.verify_password(password):
                return False
        # g.user = user_obj

        APP.config['user_id'] = user_obj.id
        APP.config['user_jwt'] = user_obj.generate_auth_token()
        return True