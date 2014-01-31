# -*- encoding: utf-8 -*-
"""Affectation pags"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, url_for, flash, redirect

import models
import forms
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/affectations/')


@bp.route('')
@requires_roles(models.BRN)
def status():
    pass


@bp.route('blocage', methods=['GET', 'POST'])
@bp.route('blocage/<int:u_id>', methods=['GET', 'POST'])
@requires_roles(models.BRN)
def block_timespan(u_id=None):
    # unavailability form + list of unavailabilities
    if u_id:
        u = models.Unavailability.query.get(u_id)
    else:
        u = models.Unavailability()

    form = forms.Unavailability(obj=u)
    if form.validate_on_submit():
        form.populate_obj(u)
        day = forms.JEUDI + timedelta(form.day.data)
        u.beginning = datetime.combine(day, form.beginning.data)
        u.end = datetime.combine(day, form.end.data)

        if not u_id:
            models.db.session.add(u)
            flash(u'Indisponibilité enregistrée')
        else:
            flash(u'Indisponibilité modifiée')

        models.db.session.commit()
        return redirect(url_for('.block_timespan'))

    if u_id:
        form.day.data = (u.beginning.date() - forms.JEUDI).days

    unavailabilities = models.Unavailability.query.all()
    unavailabilities.sort(key=lambda u: u.beginning)

    return render_template('unavailabilities.html',
                           form=form, unavailabilities=unavailabilities)


@bp.route('blocage/<int:u_id>/supprimer', methods=['GET'])
def delete_timespan_block(u_id):
    u = models.Unavailability.query.get(u_id)
    models.db.session.delete(u)
    models.db.session.commit()
    flash(u'Indisponibilité supprimée')
    return redirect(url_for('.block_timespan'))


@bp.route('automatique')
@requires_roles(models.BRN)
def automatic():
    pass
