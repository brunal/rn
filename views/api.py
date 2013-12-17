import logging

from flask import Blueprint, jsonify

from models import Responsable, Volontaire, db

RESPOS_POLES_FILE = None

bp = Blueprint(__name__, __name__, url_prefix='/api/')


@bp.route('register', methods=['POST'])
def register():
    return flask.jsonify(try_register(request.form))


def try_register(data):
    try:
        email = data['email']

        password = data['password']  # need treatement?
        user = models.User(data['email'], data['name'], -1, data['ecole'], data['portable'])

        Role = Volontaire
        with open(RESPOS_POLES_FILE, 'rb') as f:
            if email == f.readline():
                Role = Responsable

        role = Role(user)
        db.session.add(volontaire)
        db.session.commit()
        return True
    except:
        logging.exception("Cannot add user with information %s", data)
        return False
