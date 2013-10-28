#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
"""
Glues everything together and launches the app
"""
import yaml
from flask import Flask

from models import db
import views
import login

CONFIG_FILE = 'config.yaml'


def create_app():
    with open(CONFIG_FILE) as f:
        config = yaml.load(f)

    app = Flask(__name__)
    app.debug = app.config['DEBUG']
    app.secret_key = app.config['SECRET_KEY']
    app.config.update(config)

    db.init_app(app)
    login.login_manager.init_app(app)

    app.register_blueprint(views.bp)

    return app


def main():
    app = create_app()
    app.run()


if __name__ == '__main__':
    main()
