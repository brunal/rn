# -*- coding: utf-8 -*-
"""
All forms are defined here
"""
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, RadioField, validators

from models import Sexe


class Registration(Form):
    mk_req = lambda nom: [validators.Required(message=u'{} obligatoire'.format(nom))]

    email = TextField('email', validators=mk_req('email'))
    password = PasswordField('mdp', validators=mk_req('mot de passe'))
    name = TextField('nom', validators=mk_req('nom'))
    sexe = RadioField('sexe',
                      choices=[(s.value, s.name) for s in Sexe],
                      coerce=int,
                      validators=mk_req('sexe'))
    ecole = TextField(u'école', validators=mk_req(u'école'))
    portable = TextField('portable', validators=mk_req('portable'))


class Login(Form):
    email = TextField('email', validators=[validators.Required(message='email obligatoire')])
    password = PasswordField('mdp', validators=[validators.Required(message='mdp obligatoire')])
