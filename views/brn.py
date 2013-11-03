# -*- encoding: utf-8 -*-
"""
Vues pour le bureau, qui supervise
"""
from datetime import datetime, timedelta
from itertools import groupby

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

import forms
import upload
import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/brn')


@bp.route('planning')
@login_required
@requires_roles(models.BRN)
def planning_poles():
    activites = models.Activite.query.all().sort(key=lambda a: a.debut)
    return render_template('activite/planning.html', activites=activites)


@bp.route('affectations')
@login_required
@requires_roles(models.BRN)
def list_affectations():
    pass
