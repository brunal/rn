# -*- encoding: utf-8 -*-
"""
Vues pour le bureau, qui supervise
"""
from flask import Blueprint, render_template

import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/brn/')


@bp.route('sweats')
@requires_roles(models.BRN)
def sweats():
    ss = models.SweatShop()
    vols, nolimit = ss.summary_orders()
    detail_vols, detail_nolimit = ss.all_orders()
    return render_template('sweats.html',
                           vols=vols,
                           nolimit=nolimit,
                           detail_vols=detail_vols,
                           detail_nolimit=detail_nolimit)


@bp.route('affectations')
@requires_roles(models.BRN)
def affectations():
    pass
