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
    order = [None] + ss.sizes
    order_cmp = lambda x, y: order.index(x) - order.index(y)
    sort_dict = lambda d, key: sorted(d.items(), cmp=order_cmp, key=key)
    sort_those_dicts = lambda ds, key: [sort_dict(d, key) for d in ds]

    vols, nolimit = sort_those_dicts(ss.summary_orders(), lambda (k, v): k)
    detail_vols, detail_nolimit = sort_those_dicts(ss.all_orders(), lambda (k, v): v)
    return render_template('sweats.html',
                           vols=vols,
                           nolimit=nolimit,
                           detail_vols=detail_vols,
                           detail_nolimit=detail_nolimit)
