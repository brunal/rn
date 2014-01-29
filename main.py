#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
"""
Glues everything together and launches the app
"""
import os
import locale
import codecs
import logging

import yaml
from flask import Flask

import models
import login
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
        with codecs.open(os.path.join(templates, f), 'rb', 'utf8') as f_handle:
            config_mails[name] = f_handle.read()
    config['MAIL'] = config_mails

    app.config.update(config)


def create_app():
    app = Flask(__name__)

    load_config(app)

    app.debug = app.config['DEBUG']
    app.secret_key = app.config['SECRET_KEY']

    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    except locale.Error:
        logging.warning('Could not set locale')

    # init flask extensions
    mail.init_app(app)
    login.init_app(app)

    # init my modules
    models.init_app(app)
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
