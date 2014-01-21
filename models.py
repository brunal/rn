# -*- encoding: utf-8 -*-
"""
Models and database options
"""
import logging

from enum import Enum
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    SweatShop.init_app(app)


class Sexe(Enum):
    M = 1
    F = 2


class SexeActivite(Enum):
    Aucune = 0
    M = 1
    F = 2


class SweatShop(object):
    """Manage sweatshirts stocks for volontaires only"""
    shared_state = None

    def __init__(self):
        if self.shared_state:
            self.__dict__ = self.shared_state
        else:
            self.__class__.shared_state = self.__dict__
            self.stocks = self.compute_stocks()

    @classmethod
    def init_app(cls, app):
        # retrive initial stocks through the configuration
        cls.init_stocks = app.config['SWEATS']

    def _summary_orders(self):
        return db.session.query(User.sweat, func.count(User.id)).group_by(User.sweat)

    def summary_orders(self):
        so = lambda m: list(self._summary_orders().join(m))
        return dict(so(Volontaire)), dict(so(Responsable) + so(BRN))

    def all_orders(self):
        role_to_element = lambda r: (r.user.name, r.user.sweat)
        model_to_elements = lambda m: dict(map(role_to_element, m.query.all()))

        vols, respos, brns = map(model_to_elements, [Volontaire, Responsable, BRN])
        respos.update(brns)
        return vols, respos

    def compute_stocks(self):
        # retrieve user choices from the DB
        query = self._summary_orders().join(Volontaire)
        result = dict(query)
        stocks = dict(self.init_stocks)  # copy inital stocks
        for size, taken in result.items():
            if size is None:
                continue

            stocks[size] -= taken
            if stocks[size] < 0:
                logging.warning("Problem with sweats %s: %s left",
                                size, stocks[size])
        return stocks

    def try_get(self, size, user):
        if user.volontaire:
            # need to check for availability
            if self.stocks[size] <= 0:
                return False
            # there's some left
            self.stocks[size] -= 1
            if user.sweat is not None:
                self.stocks[user.sweat] += 1
        user.sweat = size
        return True

    def available(self, user):
        if user.volontaire:
            return self.stocks.keys()
        else:
            return [s for s, count in self.stocks.items() if count > 0]


class Disponibilite(Enum):
    JA = 1
    VM = 2
    VA = 3
    LM = 4

    def __str__(self):
        if self is Disponibilite.JA:
            return u"jeudi après-midi"
        elif self is Disponibilite.VM:
            return u"vendredi matin"
        elif self is Disponibilite.VA:
            return u"vendredi après-midi"
        elif self is Disponibilite.LM:
            return u"lundi matin"


# Profils utilisateurs


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)

    _sexe = db.Column(db.Integer)
    sweat = db.Column(db.String)
    ecole = db.Column(db.String)
    portable = db.Column(db.String)

    @property
    def sexe(self):
        return self._sexe

    @sexe.setter
    def sexe(self, s):
        if isinstance(s, int):
            self._sexe = s
        else:
            self._sexe = s.value

    def get_sexe(self):
        return Sexe(self._sexe)

    def show_sexe(self):
        return self.get_sexe().name

    def try_get_sweat(self, sweat):
        return SweatShop().try_get(sweat, self)

    def available_sweats(self):
        return SweatShop().available(self)

    def __init__(self, email, password, name, sexe, ecole, portable):
        self.email = email
        self.password = password
        self.name = name
        self.sexe = sexe
        self.sweat = None
        self.ecole = ecole
        self.portable = portable

    def __repr__(self):
        return "{}(id={}, email={})".format(self.__class__.__name__, self.id, self.email)

    def __str__(self):
        return self.email

    @property
    def role(self):
        return self.volontaire or self.responsable or self.brn


class Volontaire(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('volontaire', uselist=False))

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user):
        self.user = user

    def is_affected_to(self, a_id):
        return Affectation.query.filter((Affectation.activite_id == a_id) &
                                        (Affectation.volontaire_id == self.id)).count() > 0

    @property
    def activites(self):
        return [aff.activite for aff in self.affectations]

    @property
    def planning(self):
        return (self.activites + Planning.query.all()).sort(key=lambda e: e.debut)

    def __repr__(self):
        return "{}(user_id={})".format(self.__class__.__name__, self.user_id)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.user)


class Disponibilites(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # semble obligatoire
    volontaire_id = db.Column(db.Integer, db.ForeignKey('volontaire.id'))
    volontaire = db.relationship('Volontaire', backref=db.backref('disponibilites'))
    quand = db.Column(db.Integer)

    def __init__(self, volontaire, quand):
        self.volontaire = volontaire
        self.quand = quand

    def __repr__(self):
        return "{}(volontaire_id={}, quand={})" \
                .format(self.__class__.__name__, self.volontaire_id, self.quand)

    def __str__(self):
        return "{} dispo le {}".format(self.volontaire.user.email, self.quand)


class Responsable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('responsable', uselist=False))

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return "{}(user_id={})".format(self.__class__.__name__, self.user_id)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.user)


class BRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('brn', uselist=False))

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return "{}(user_id={})".format(self.__class__.__name__, self.user_id)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, self.user)


# Planning et activités

class Evenement(object):
    debut = db.Column(db.DateTime)
    fin = db.Column(db.DateTime)
    lieu = db.Column(db.String)
    nom = db.Column(db.String)


class Activite(db.Model, Evenement):
    id = db.Column(db.Integer, primary_key=True)
    responsable_id = db.Column(db.Integer, db.ForeignKey('responsable.id'))
    responsable = db.relationship('Responsable', backref=db.backref('activites'))

    description = db.Column(db.Text)
    nombre_volontaires = db.Column(db.Integer)
    _sexe = db.Column(db.Integer)

    @property
    def sexe(self):
        return self._sexe

    @sexe.setter
    def sexe(self, s):
        if isinstance(s, int):
            self._sexe = s
        else:
            self._sexe = s.value

    def get_sexe(self):
        return SexeActivite(self._sexe)

    def show_sexe(self):
        return self.get_sexe().name


class Affectation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    volontaire_id = db.Column(db.Integer, db.ForeignKey('volontaire.id'))
    volontaire = db.relationship('Volontaire', backref=db.backref('affectations'))

    activite_id = db.Column(db.Integer, db.ForeignKey('activite.id'))
    activite = db.relationship('Activite', backref=db.backref('affectations'))


class Planning(db.Model, Evenement):
    id = db.Column(db.Integer, primary_key=True)
