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
    # misc. stats
    activites = models.Activite.query.all()
    vols = models.Volontaire.query.count()
    slots = sum(a.nombre_volontaires for a in activites)
    assign_auto = models.Assignement.auto().count()
    assign_manual = models.Assignement.manual().count()

    tot_help_time = sum((a.nombre_volontaires * (a.fin - a.debut) for a in activites), timedelta())

    return render_template('assignements/status.html',
                           activites=len(activites),
                           vols=vols,
                           slots=slots,
                           assign_auto=assign_auto,
                           assign_manual=assign_manual,
                           avg_slot_length=tot_help_time / slots,
                           avg_help_time=tot_help_time / vols)


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

        # conflict check
        for activite in u.conflicts():
            flash(u"Suppression de l'affectation à '%s'" % activite.nom)
            assignement = next(a for a in u.volontaire.assignements
                               if a.activite == activite)
            models.db.session.delete(assignement)

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

    return render_template('assignements/unavailabilities.html',
                           form=form, unavailabilities=unavailabilities)


@bp.route('blocage/<int:u_id>/supprimer', methods=['GET'])
def delete_timespan_block(u_id):
    u = models.Unavailability.query.get(u_id)
    models.db.session.delete(u)
    models.db.session.commit()
    flash(u'Indisponibilité supprimée')
    return redirect(url_for('.block_timespan'))


@bp.route('manuel')
@requires_roles(models.BRN)
def manual():
    assignements = list(models.Assignement.manual())
    assignements.sort(key=lambda a: (a.volontaire.user.name, a.activite.debut))
    return render_template('assignements/manual.html',
                           assignements=assignements)


@bp.route('automatique')
@requires_roles(models.BRN)
def automatic():
    return render_template('future.html')
