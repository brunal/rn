"""
Tools related to user authentication & login
"""
from hashlib import md5
from functools import wraps
import logging

from flask import abort
from flask.ext.login import LoginManager, UserMixin, current_user, login_required

import models

MD5_FMT = None

login_manager = LoginManager()


def init_app(app):
    global MD5_FMT
    MD5_FMT = app.config['MD5_FMT']
    app.context_processor(inject_roles)
    login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_model):
        self.user = user_model

    def get_id(self):
        return unicode(self.user.id)

    @classmethod
    def get(cls, uid):
        try:
            id = int(uid)
            userm = models.User.query.get(id)
        except:
            logging.exception("Cannot retrieve user from uid %s (type %s)", uid, type(uid))
            return None

        obj = cls(userm)
        return obj


def hash_password(password):
    return md5(MD5_FMT % password).hexdigest()


def authentify(email, password):
    hashed_pass = hash_password(password)
    resp = models.User.query.filter_by(email=email, password=hashed_pass).first()
    if not resp:
        return None
    return User(resp)


def change_password(email, new_pwd):
    user = models.User.query.filter_by(email=email).first()
    if user is not None:
        user.password = new_pwd
        models.db.session.commit()
    return user is not None


@login_manager.user_loader
def load_user(id):
    logging.debug("Trying to log user with id %s", id)
    return User.get(id)


def requires_roles(*roles):
    """Authorization decorator"""
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if any(Role.query.filter_by(user=current_user.user).first()
                   for Role in roles):
                return f(*args, **kwargs)
            abort(401)
        return login_required(wrapped)
    return wrapper


def inject_roles():
    if not current_user.is_authenticated():
        return {}
    u = current_user.user
    return {'volontaire': bool(u.volontaire),
            'responsable': bool(u.responsable),
            'brn': bool(u.brn)}
