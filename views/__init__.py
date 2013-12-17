from basic import config as config_basic, \
                  bp as bp_basic  # register login logout profil
from responsable import bp as bp_responsable  # activities management
from activite import bp as bp_activite  # activities for non-manager
from brn import bp as bp_brn  # supervision for BRN members
from api import bp as bp_api  # registration API

all_blueprints = [bp_basic, bp_responsable, bp_activite, bp_basic, bp_api]


def init_app(app):
    """Central initialization function for view modules"""
    config_basic.REGISTRATION_EMAIL_TEMPLATE = app.config['MAIL']['REGISTRATION']
    RESPOS_POLES_FILE = app.config['RESPOS_POLES_FILE']
