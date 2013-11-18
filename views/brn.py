# -*- encoding: utf-8 -*-
"""
Vues pour le bureau, qui supervise
"""
from flask import Blueprint, render_template

import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/brn/')


@bp.route('affectations')
@requires_roles(models.BRN)
def affectations():
    pass
