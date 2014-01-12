#-*- encoding: utf-8 -*-
import logging

from flask import Blueprint, jsonify, request, url_for
from flask_mail import Message

from models import User, Responsable, Volontaire, db
from lib import mail

RESPOS_POLES_FILE = None
REGISTRATION_EMAIL_TEMPLATE = None

bp = Blueprint(__name__, __name__, url_prefix='/api/')


def send_registration_email(user):
    msg = Message(u'Inscription volontaire RN réussie', recipients=[user.email])
    msg.body = REGISTRATION_EMAIL_TEMPLATE.format(nom=user.name,
                        profil=url_for('views.basic.profil', _external=True),
                        index=url_for('views.basic.index', _external=True))
    mail.send(msg)


@bp.route('register', methods=['POST'])
def register():
    user = jsonify({'response': try_register(request.form)})
    if user:
        send_registration_email(user)
    return bool(user)


def try_register(data):
    try:
        email = data['email']
        password = data['password']
        user = User(email, password, data['name'], -1, data['ecole'], data['portable'])

        Role = Volontaire
        with open(RESPOS_POLES_FILE, 'rb') as f:
            if email == f.readline():
                Role = Responsable

        role = Role(user)
        db.session.add(role)
        db.session.commit()

        return user
    except:
        logging.exception("Cannot add user with information %s", data)
        return False
