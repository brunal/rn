# -*- encoding: utf-8 -*-
"""
Models and database options
"""
import logging
from collections import Counter
from datetime import timedelta

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
        so = lambda m: dict(self._summary_orders().join(m))
        return so(Volontaire), dict(Counter(so(Responsable)) + Counter(so(BRN)))

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
            return [s for s, count in self.stocks.items() if count > 0]
        else:
            return self.stocks.keys()

    @property
    def sizes(self):
        return self.stocks.keys()


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
        if isinstance(s, int) or s is None:
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

    def __init__(self, email, password, name, ecole, portable):
        self.email = email
        self.password = password
        self.name = name
        self.sexe = None
        self.sweat = None
        self.ecole = ecole
        self.portable = portable

    def __repr__(self):
        return "{}(id={}, email={})".format(self.__class__.__name__, self.id, self.email)

    def __str__(self):
        return self.email

    @property
    def role(self):
        return self.responsable or self.volontaire or self.brn


class Volontaire(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('volontaire', uselist=False))

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user):
        self.user = user

    def is_affected_to(self, a_id):
        return Assignement.query.filter((Assignement.activite_id == a_id) &
                                        (Assignement.volontaire_id == self.id)).count() > 0

    @classmethod
    def manually_assigned_to(cls, activite):
        return [a.volontaire for a in Assignement.query.filter_by(activite_id=activite, source=Assignement.MANUAL)]

    def check_conflicts(self):
        all_conflicts = []
        acts = self.activites
        for a, rest in ((act, acts[i + 1:]) for i, act in enumerate(acts)):

            overlaps = a.overlaps_with(rest)
            for o in overlaps:
                all_conflicts.append((a, o))
        return all_conflicts

    @property
    def activites(self):
        return [aff.activite for aff in self.assignements]

    @property
    def help_time(self):
        return sum((a.fin - a.debut for a in self.activites), timedelta())

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

    @classmethod
    def all(cls):
        """Return all items sorted by beginning date"""
        return cls.query.order_by(cls.debut)

    @classmethod
    def most_in_need_of_help(cls):
        need_help = [a for a in cls.all()
                     if len(a.assignees) < a.nombre_volontaires]
        # sort by filling percentage + low need of help
        key = lambda a: (len(a.assignees) / float(a.nombre_volontaires),
                         a.nombre_volontaires)
        return sorted(need_help, key=key)

    @property
    def assignees(self):
        return [ass.volontaire for ass in self.assignements]

    def manual_assignements(self):
        return Assignement.query.filter_by(activite_id=self.id, source=Assignement.MANUAL)

    def get_available_volontaires(self):
        # FIXME
        return sorted([v for v in Volontaire.query.all() if
                       not self.overlaps_with(v.activites, _bool=True) and
                       not any(self.conflicts(u.beginning, u.end, [self], _bool=True)
                               for u in v.unavailabilities)],
                      key=lambda v: v.user.name)

    def overlaps_with(self, activites, _bool=False):
        return self.conflicts(self.debut, self.fin, activites, _bool)

    @classmethod
    def conflicts(cls, beginning, end, activites, _bool=False):
        """Checks whether a time span conflicts with `activites`

        Returns
        -------
        conflicts : Activite list
        """
        conflicts = []
        for a in activites:
            if a.debut <= beginning <= a.fin or \
               beginning <= a.debut <= end:
                if _bool:  # I just want the answer!
                    return True
                conflicts.append(a)
        return conflicts


class Assignement(db.Model):
    AUTOMATIC = 1
    MANUAL = 2

    id = db.Column(db.Integer, primary_key=True)

    volontaire_id = db.Column(db.Integer, db.ForeignKey('volontaire.id'))
    volontaire = db.relationship('Volontaire', backref=db.backref('assignements'))

    activite_id = db.Column(db.Integer, db.ForeignKey('activite.id'))
    activite = db.relationship('Activite', backref=db.backref('assignements'))

    # 1 for automatic, 2 for manual
    source = db.Column(db.Integer)

    @property
    def is_manual(self):
        return self.source == self.MANUAL

    @classmethod
    def auto(cls):
        return cls.query.filter(cls.source == cls.AUTOMATIC)

    @classmethod
    def manual(cls):
        return cls.query.filter(cls.source == cls.MANUAL)


class Unavailability(db.Model):
    """Used for a Volontaire unavailable on a time span"""
    id = db.Column(db.Integer, primary_key=True)

    volontaire_id = db.Column(db.Integer, db.ForeignKey('volontaire.id'))
    volontaire = db.relationship('Volontaire', backref=db.backref('unavailabilities'))

    reason = db.Column(db.String)
    beginning = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def conflicts(self):
        return Activite.conflicts(self.beginning, self.end,
                                  self.volontaire.activites)


class Planning(db.Model, Evenement):
    id = db.Column(db.Integer, primary_key=True)
