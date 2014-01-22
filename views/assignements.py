# -*- encoding: utf-8 -*-
"""Affectation pags"""
from flask import Blueprint, render_template

import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/affectations/')


@bp.route('')
@requires_roles(models.BRN)
def status():
    pass


@bp.route('blocage')
@requires_roles(models.Responsable, models.BRN)
def block_timespan():
    pass


@bp.route('automatique')
@requires_roles(models.BRN)
def automatic():
    pass
