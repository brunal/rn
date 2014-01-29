# -*- encoding: utf-8 -*-
#!/usr/bin/env python2
"""
Small functions for convenience
"""
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
