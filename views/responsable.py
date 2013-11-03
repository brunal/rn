# -*- encoding: utf-8 -*-
"""
Vues pour les responsables : gestion d'un pôle
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask.ext.login import login_required, current_user

import forms
import upload
import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/responsable/')


# Gestion de l'activité, réservée à son responsable

def get_activite(id):
    activite = models.Activite.query.get(id) or abort(404)
    if activite.responsable != current_user.user.role:
        abort(401)
    return activite


@bp.route('')
@login_required
@requires_roles(models.Responsable)
def list_activites():
    activites = models.Activite.query.filter(models.Responsable.id == current_user.user.role.id)
    # check which ones are incomplete
    misconfigured = []
    correct = []
    for a in activites:
        if not a.nom or not a.lieu or not a.debut or not a.fin or not a.nombre_volontaires:
            misconfigured.append(a)
        else:
            correct.append(a)
    return render_template('responsable_activites.html', activites=correct, misconfigured=misconfigured)


@bp.route('nouvelle')
@login_required
@requires_roles(models.Responsable)
def add_activite():
    activite = models.Activite()
    activite.responsable = current_user.user.role
    models.db.session.add(activite)
    models.db.session.commit()
    flash(u'Activité créée')
    return redirect(url_for('.activite_get', a_id=activite.id))


@bp.route('<int:a_id>/')
@login_required
@requires_roles(models.Responsable)
def activite_get(a_id):
    activite = get_activite(a_id)
    form = forms.Activite(obj=activite)
    if activite.debut:
        form.jour.data = (activite.debut.date() - forms.JEUDI).days
    return render_template('config_activite.html', form=form, a_id=activite.id,
                           files=upload.list_files(activite.id),
                           extensions=upload.config.ALLOWED_EXTENSIONS)


@bp.route('<int:a_id>/', methods=['POST'])
@login_required
@requires_roles(models.Responsable)
def activite_post(a_id):
    form = forms.Activite(request.form)
    if form.validate():
        activite = get_activite(a_id)
        form.populate_obj(activite)

        jour = forms.JEUDI + timedelta(form.jour.data)
        activite.debut = datetime.combine(jour, form.debut.data)
        activite.fin = datetime.combine(jour, form.fin.data)

        flash(u'Activité mise à jour')
        models.db.session.commit()

        redirect(url_for('.activite_get', a_id=activite.id))

    return render_template('config_activite.html', form=form,
                           files=upload.list_files(activite.id),
                           extensions=upload.config.ALLOWED_EXTENSIONS)


@bp.route('<int:a_id>/upload', methods=['POST'])
@login_required
@requires_roles(models.Responsable)
def upload_page(a_id):
    activite = get_activite(a_id)
    files = request.files.getlist('files')
    successes, failures = upload.upload_files(activite.id, files)
    if successes:
        flash(u'Succès : {}'.format(', '.join(successes)))
    if failures:
        flash(u'Echecs : {}'.format(', '.join(failures)))
    return redirect(url_for('.activite_get'), a_id=activite.id)


@bp.route('<int:a_id>/delete/')
@login_required
@requires_roles(models.Responsable)
def delete_activite(a_id):
    activite = get_activite(a_id)
    models.db.session.delete(activite)
    models.db.session.commit()
    flash(u'Activité supprimée')
    return redirect(url_for('.list_activites'))


@bp.route('<int:a_id>/delete/<filename>')
@login_required
@requires_roles(models.Responsable)
def delete_asset(a_id, filename):
    activite = get_activite(a_id)
    result = upload.delete_file(activite.id, filename)
    if result is True:
        flash(u'{} a bien été supprimé'.format(filename))
    else:
        # result is an error message
        flash('Impossible de supprimer {} car {}'.format(filename, result))
    return redirect(url_for('.activite_get', a_id=activite.id))
