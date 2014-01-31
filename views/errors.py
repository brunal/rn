# -*- encoding: utf-8 -*-
from flask import render_template


def init_app(app):
    register_handler(app, 403)
    register_handler(app, 404)
    register_handler(app, 500)


def register_handler(app, num):
    app.errorhandler(num)(make_handler(num))


def make_handler(err_num):
    def handler(error):
        return render_template('error.html', error=err_num), err_num
    return handler
