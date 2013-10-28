"""
Models and database options
"""
from enum import Enum
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def db_init(app):
    db.init_app(app)


class Sexe(Enum):
    M = 1
    F = 2


class Sweat(Enum):
    XS = 1
    S = 2
    M = 3
    L = 4
    XL = 5
    XXL = 6


class Disponibilite(Enum):
    JA = 1
    VM = 2
    VA = 3
    LM = 4


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)

    sexe = db.Column(db.Integer)
    ecole = db.Column(db.String)
    portable = db.Column(db.String)

    def __init__(self, email, password, name, sexe, ecole, portable):
        self.email = email
        self.password = password
        self.name = name
        self.sexe = sexe
        self.ecole = ecole
        self.portable = portable

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.email)


class Volontaire(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('volontaire'), uselist=False)

    id = db.Column(db.Integer, primary_key=True)
    sweat = db.Column(db.Integer)

    def __init__(self, user, sweat=None):
        self.user = user
        self.sweat = sweat


class Disponibilites(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # semble obligatoire
    volontaire_id = db.Column(db.Integer, db.ForeignKey('volontaire.id'))
    volontaire = db.relationship('Volontaire', backref=db.backref('disponibilites'))
    quand = db.Column(db.Integer)

    def __init__(self, volontaire, quand):
        self.volontaire = volontaire
        self.quand = quand


class Responsable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('responsable'), uselist=False)

    def __init__(self, user):
        self.user = user


class BRN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('brn'), uselist=False)

    def __init__(self, user):
        self.user = user
