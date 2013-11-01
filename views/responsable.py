# -*- encoding: utf-8 -*-
"""
Vus pour les responsables : gestion d'un pôle
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

import forms
import models
from login import requires_roles


bp = Blueprint(__name__, __name__)


@bp.route('/responsable')
@login_required
@requires_roles(models.Responsable)
def activite_get():
    activite = current_user.user.role.activite
    if activite:
        form = forms.Activite(obj=activite)
        form.jour.data = (activite.debut.date() - forms.JEUDI).days
    else:
        form = forms.Activite()

    return render_template('activite.html', form=form)


@bp.route('/responsable', methods=['POST'])
@login_required
@requires_roles(models.Responsable)
def activite_post():
    form = forms.Activite(request.form)
    if form.validate():
        # màj ou nouvel objet ?
        activite = current_user.user.role.activite
        if activite:
            flash(u'Activité mise à jour')
        else:
            activite = models.Activite()
            activite.responsable = current_user.user.role
            models.db.session.add(activite)
            flash(u'Activité enregistrée')

        form.populate_obj(activite)
        jour = forms.JEUDI + timedelta(form.jour.data)
        activite.debut = datetime.combine(jour, form.debut.data)
        activite.fin = datetime.combine(jour, form.fin.data)

        models.db.session.commit()

        redirect(url_for('.activite_get'))

    return render_template('activite.html', form=form)
