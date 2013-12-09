# -*- coding: utf-8 -*-
"""
All forms are defined here
"""
from datetime import date

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, RadioField, DateTimeField, \
                    SelectMultipleField, SelectField, TextAreaField, \
                    IntegerField, validators, widgets

from models import Sexe, SexeActivite, Sweat, Disponibilite


def mk_req(nom):
    return [validators.DataRequired(message=u'{} obligatoire'.format(nom))]


# Utilisateurs

class Registration(Form):

    email = StringField('email', validators=mk_req('email'))
    password = PasswordField('mot de passe',
                             validators=[validators.Required(message=u'Mot de passe obligatoire'),
                                         validators.Length(min=5, message=u'Minimum %(min)d caractères')])
    password2 = PasswordField(u'répéter le mot de passe',
                              validators=[validators.EqualTo(fieldname='password',
                                                             message=u'Les deux mots de passe doivent être égaux')])
    name = StringField('nom', validators=mk_req('nom'))
    sexe = RadioField('sexe',
                      choices=[(s.value, s.name) for s in Sexe],
                      coerce=int,
                      validators=mk_req('sexe'))
    ecole = StringField(u'école', validators=mk_req(u'école'))
    portable = StringField('portable', validators=mk_req('portable'))


class Login(Form):
    email = StringField('email', validators=mk_req('email'))
    password = PasswordField('mdp', validators=mk_req('mdp'))


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Profil(Form):
    sweat = RadioField('sweat',
                      choices=[(s.value, s.name) for s in Sweat],
                      coerce=int,
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
    jour = SelectField('jour', coerce=int,
                       choices=[(0, 'jeudi'), (1, 'vendredi'),
                                (2, 'samedi'), (3, 'dimanche'), (4, 'lundi')])
    debut = DateTimeField(u'heure de début (HH:MM)', validators=mk_req(u'début'),
                          format='%H:%M', filters=(time_or_none,))
    fin = DateTimeField('heure de fin (HH:MM)', validators=mk_req(u'fin'),
                        format='%H:%M', filters=(time_or_none,))

    nom = StringField(u'nom de l\'activité', validators=mk_req('nom'))
    description = TextAreaField(u'description de l\'activité', validators=mk_req('description'))
    lieu = StringField('lieu', validators=mk_req('lieu'))
    nombre_volontaires = IntegerField(u'nombre de volontaires demandé')
    sexe = RadioField(u'préférence quant au sexe des volontaires',
                      choices=[(s.value, s.name) for s in SexeActivite],
                      coerce=int)
