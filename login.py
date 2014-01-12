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
        except Exception as e:
            logging.debug("Cannot retrieve user from uid %s (type %s)", uid, type(uid))
            logging.debug(e)
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


@login_manager.user_loader
def load_user(id):
    logging.debug("Trying to log user with id %s", id)
    return User.get(id)


def get_current_user_role():
    return type(current_user.user.role)


def requires_roles(*roles):
    """Authorization decorator"""
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if get_current_user_role() not in roles:
                abort(401)
            return f(*args, **kwargs)
        return login_required(wrapped)
    return wrapper


def inject_roles():
    role = current_user.is_authenticated() and get_current_user_role() or None
    return {'volontaire': role is models.Volontaire,
            'responsable': role is models.Responsable,
            'brn': role is models.BRN}
