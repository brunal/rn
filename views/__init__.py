from basic import bp as bp_basic  # register login logout profil
from responsable import bp as bp_responsable  # activities management
from activite import bp as bp_activite  # activities for non-manager
from brn import bp as bp_brn  # supervision for BRN members
from assignements import bp as bp_assign  # activities assignements
import api  # registration API

all_blueprints = [bp_basic, bp_responsable, bp_brn, bp_activite, bp_basic, bp_assign, api.bp]


def set_from_file(path):
    with open(path, 'rb') as f:
        return set(f.read().splitlines())


def init_app(app):
    """Central initialization function for view modules"""
    api.REGISTRATION_EMAIL_TEMPLATE = app.config['MAIL']['REGISTRATION']

    api.RESPOS_POLES = set_from_file(app.config['RESPOS_POLES_FILE'])
    api.BRNS = set_from_file(app.config['BRN_FILE'])
