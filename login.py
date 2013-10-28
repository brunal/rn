"""
Tools related to user authentication & login
"""
from hashlib import sha1
import logging

from flask.ext.login import LoginManager, UserMixin

import models


login_manager = LoginManager()


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
    return sha1(password).hexdigest()


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
