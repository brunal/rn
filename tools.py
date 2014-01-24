# -*- encoding: utf-8 -*-
#!/usr/bin/env python2
"""
Small functions for convenience
"""
import csv

from main import *
from models import *
import login

app = create_app()
app.test_request_context().push()


def add_users():
    """
    Create the DB & add 3 fake users
    """
    def make_u(r):
        return User('%s@test' % r, login.hash_password(r), r, '%s%s' % (r, r), '00 00 00 00 00')

    db.create_all()

    v = Volontaire(make_u('un'))
    r = Responsable(make_u('deux'))
    b = BRN(make_u('trois'))

    map(db.session.add, [v, r, b])
    db.session.commit()
    print u"ajouté :", v, r, b

def fix_name():
    fname = 'volontaires.csv'
    with open(fname, 'rb') as f:
        content = csv.reader(f, delimiter='\t')
        for nom, prenom, _, email in content:
            u = User.query.filter_by(email=email).first()
            if u is None:
                print "no account"
                continue

            new_name = fix_name_format(prenom, nom)
            print u"%s -> %s" % (u.name, new_name)
            u.name = new_name
        db.session.commit()

def fix_name_format(prenom, nom):
    name_parts = nom.split()
    new_name = [prenom]
    for np in name_parts:
        np = np[0].upper() + np[1:].lower()
        if np == u'De':
            np = u'de'
        elif np == u'Du':
            np = u'du'
        new_name.append(np)
    new_name = [n.decode('utf8') for n in new_name]
    return ' '.join(new_name)
