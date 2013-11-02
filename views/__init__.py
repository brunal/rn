from basic import config as config_basic, \
                  bp as bp_basic  # register login logout profil
from responsable import bp as bp_responsable  # activities management
from activite import bp as bp_activite  # activities for non-manager


def init_app(app):
    """Central initialization function for view modules"""
    config_basic.REGISTRATION_EMAIL_TEMPLATE = app.config['MAIL']['REGISTRATION']
