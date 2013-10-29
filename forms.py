# -*- coding: utf-8 -*-
"""
All forms are defined here
"""
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, RadioField, validators, SelectMultipleField, widgets

from models import Sexe, Sweat, Disponibilite


def mk_req(nom):
    return [validators.Required(message=u'{} obligatoire'.format(nom))]


class Registration(Form):

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


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Profil(Form):
    sweat = RadioField('sweat',
                      choices=[(s.value, s.name) for s in Sweat],
                      coerce=int,
                      validators=mk_req('sweat'))
    disponibilites = MultiCheckboxField('disponibilites',
                      choices=[(s.value, s) for s in Disponibilite],
                      coerce=int)
