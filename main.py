#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
"""
Glues everything together and launches the app
"""
import os
import yaml

from flask import Flask

from models import db
from login import login_manager, inject_roles
import views
from lib import upload, filters, mail


CONFIG_FILE = 'config.yaml'


def load_config(app):
    # take config from file
    with open(CONFIG_FILE) as f:
        config = yaml.load(f)

    # load email templates
    templates = config['MAIL_TEMPLATES']
    config_mails = dict()
    for f in os.listdir(templates):
        name = os.path.splitext(f)[0].upper()
        # load template content in config
        with open(os.path.join(templates, f), 'rb') as f_handle:
            config_mails[name] = f_handle.read()
    config['MAIL'] = config_mails

    app.config.update(config)


def create_app():
    app = Flask(__name__)

    load_config(app)

    app.debug = app.config['DEBUG']
    app.secret_key = app.config['SECRET_KEY']

    # init flask extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    app.context_processor(inject_roles)

    # init my modules
    upload.init_app(app)
    filters.init_app(app)
    views.init_app(app)

    # register routes
    map(app.register_blueprint, views.all_blueprints)

    return app


def main():
    app = create_app()
    app.run()


if __name__ == '__main__':
    main()
