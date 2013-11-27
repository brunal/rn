#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
"""
Simple script to create Responsable & BRN accounts
"""
import csv
from sys import argv

from flask import url_for
from flask_mail import Message

from main import create_app
from models import db, User, Responsable, BRN, Sexe
from lib import mail


def send_email(m):
    msg = Message('Inscription {} RN réussie'.format(m.__class__.__name__),
                  recipients=[m.user.email])
    msg.body = "Bonjour {}. Ton inscription au site des volontaires de la RN ({}) \
a bien été enregistrée.\n \
Cordialement.".format(m.user.name, url_for('views.basic.index', _external=True))
    mail.send(msg)


def add(model, f):
    app = create_app()
    app.test_request_context().push()
    for line in csv.reader(f):
        if not line:
            # skip empty lines
            continue
        line = [unicode(l, 'utf_8') for l in line]
        try:
            email, password, name, sexe, ecole, portable = line
        except ValueError:
            raise ValueError("La ligne semble trop courte (sur {}) !".format(line))

        try:
            sexe = Sexe[sexe].value
        except:
            raise ValueError("sexe: reçu {} au lieu de M ou F pour {}".format(sexe, name))
        u = User(email, password, name, sexe, ecole, portable)
        m = model(u)
        db.session.add(m)
        print "Créé {}".format(m)

        send_email(m)
    db.session.commit()
    print "Tout s'est bien passé !"


def main():
    if len(argv) == 3:
        target = argv[1]
        if target in ["responsable", "brn"]:
            if target == "responsable":
                model = Responsable
            else:
                model = BRN
            try:
                with open(argv[2], 'rb') as f:
                    add(model, f)
                    return
            except Exception:
                usage()
                print "cause de l'erreur (si vous ne comprenez pas, appelez un geek) :"
                raise
        usage()


def usage():
    # something went wrong
    print "Usage: {} [responsable|brn] fichier.csv".format(argv[0])
    print "dans le fichier: email mdp nom sexe ecole portable"
    print "sexe: M ou F"


if __name__ == '__main__':
    main()
