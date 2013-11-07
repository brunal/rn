# -*- encoding: utf-8 -*-
"""
Vues pour le bureau, qui supervise
"""
from flask import Blueprint, render_template

import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/brn')


@bp.route('planning')
@requires_roles(models.BRN)
def planning_poles():
    activites = models.Activite.query.all().sort(key=lambda a: a.debut)
    return render_template('activite/planning.html', activites=activites)


@bp.route('affectations')
@requires_roles(models.BRN)
def list_affectations():
    pass
