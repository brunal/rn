# -*- coding: utf-8 -*-
"""
All forms are defined here
"""
from datetime import date

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, RadioField, DateTimeField, \
                    SelectMultipleField, SelectField, TextAreaField, \
                    IntegerField, validators, widgets

from models import Sexe, SexeActivite, Disponibilite


def mk_req(nom):
    return [validators.DataRequired(message=u'{} obligatoire'.format(nom))]


# Utilisateurs

class Login(Form):
    email = StringField('email', validators=mk_req('email'))
    password = PasswordField('mdp', validators=mk_req('mdp'))


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Profil(Form):
    """Profile page form

    `sexe` will only be rendered if user is a Volontaire and has not sexe `sexe`
    `disponibilites` will only be rendered if user is a Volontaire
    This is done if `views.basic.profil`
    """
    sexe = RadioField('sexe',
                      choices=[(s.value, s.name) for s in Sexe],
                      coerce=int)
    sweat = RadioField('sweat',
                      choices=[],
                      coerce=str,
                      validators=mk_req('sweat'))
    disponibilites = MultiCheckboxField(u'disponibilités supplémentaires',
                      choices=[(s.value, s) for s in Disponibilite],
                      coerce=int)


# Activités

# début de la RN
JEUDI = date(2014, 2, 1)


def time_or_none(t):
    if t is None:
        return None
    return t.time()


class Activite(Form):
    nom = StringField(u'nom de l\'activité', validators=mk_req('nom'))
    jour = SelectField('jour', coerce=int,
                       choices=[(0, 'jeudi'), (1, 'vendredi'),
                                (2, 'samedi'), (3, 'dimanche'), (4, 'lundi')])
    debut = DateTimeField(u'début (HH:MM)', validators=mk_req(u'début'),
                          format='%H:%M', filters=(time_or_none,))
    fin = DateTimeField('fin (HH:MM)', validators=mk_req(u'fin'),
                        format='%H:%M', filters=(time_or_none,))

    description = TextAreaField(u'description de l\'activité', validators=mk_req('description'))
    lieu = StringField('lieu', validators=mk_req('lieu'))
    nombre_volontaires = IntegerField(u'nombre de volontaires demandé')
    sexe = RadioField(u'préférence quant au sexe des volontaires',
                      choices=[(s.value, s.name) for s in SexeActivite],
                      coerce=int)


class ManualActiviteAssignement(Form):
    people = SelectMultipleField('Volontaires', coerce=int)
