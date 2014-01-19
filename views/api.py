#-*- encoding: utf-8 -*-
import logging

from flask import Blueprint, jsonify, request, url_for
from flask_mail import Message

from models import User, BRN, Responsable, Volontaire, db
from login import change_password
from lib import mail

RESPOS_POLES = None
BRNS = None
REGISTRATION_EMAIL_TEMPLATE = None

bp = Blueprint(__name__, __name__, url_prefix='/api/')


def send_registration_email(user):
    msg = Message(u'Inscription volontaire RN réussie', recipients=[user.email])
    msg.body = REGISTRATION_EMAIL_TEMPLATE.format(nom=user.name,
                        profil=url_for('views.basic.profil', _external=True),
                        index=url_for('views.basic.index', _external=True))
    mail.send(msg)


@bp.route('change-password', methods=['POST'])
def changepassword():
    try:
        email = request.form['email']
        old_pwd = request.form['old_password']
        new_pwd = request.form['new_password']
        result = change_password(email, old_pwd, new_pwd)
    except:
        logging.exception("Cannot change password with information %s", request.form)
        result = 'exception'

    return jsonify({'response': result})


@bp.route('register', methods=['POST'])
def register():
    user = try_register(request.form)
    if user:
        send_registration_email(user)
    return jsonify({'response': bool(user)})


def try_register(data):
    try:
        email = data['email']
        password = data['password']
        user = User(email, password, data['name'], -1, data['ecole'], data['portable'])

        if email in RESPOS_POLES:
            role = Responsable(user)
        elif email in BRNS:
            role = BRN(user)
        else:
            role = Volontaire

        db.session.add(role)
        db.session.commit()

        return user
    except:
        logging.exception("Cannot add user with information %s", data)
        return False
