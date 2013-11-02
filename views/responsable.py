# -*- encoding: utf-8 -*-
"""
Vues pour les responsables : gestion d'un pôle
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user

import forms
import upload
import models
from login import requires_roles


bp = Blueprint(__name__, __name__, url_prefix='/')


# Gestion de l'activité, réservée à son responsable

@bp.route('responsable')
@login_required
@requires_roles(models.Responsable)
def activite_get():
    activite = current_user.user.role.activite
    if activite:
        form = forms.Activite(obj=activite)
        form.jour.data = (activite.debut.date() - forms.JEUDI).days
        return render_template('config_activite.html', form=form,
                               files=upload.list_files(activite.id),
                               extensions=upload.config.ALLOWED_EXTENSIONS)
    else:
        form = forms.Activite()
        # on ne propose pas le téléversement si l'activité n'a pas été créée
        return render_template('config_activite.html', form=form)


@bp.route('responsable', methods=['POST'])
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

    return render_template('config_activite.html', form=form,
                           files=upload.list_files(activite.id),
                           extensions=upload.config.ALLOWED_EXTENSIONS)


@bp.route('upload', methods=['POST'])
@login_required
@requires_roles(models.Responsable)
def upload_page():
    files = request.files.getlist('files')
    successes, failures = upload.upload_files(current_user.user.role.activite.id, files)
    if successes:
        flash(u'Succès : {}'.format(', '.join(successes)))
    if failures:
        flash(u'Echecs : {}'.format(', '.join(failures)))
    return redirect(url_for('.activite_get'))


@bp.route('delete/<filename>')
@login_required
@requires_roles(models.Responsable)
def delete_asset(filename):
    result = upload.delete_file(current_user.user.role.activite.id, filename)
    if result is True:
        flash(u'{} a bien été supprimé'.format(filename))
    else:
        # result is an error message
        flash('Impossible de supprimer {} car {}'.format(filename, result))
    return redirect(url_for('.activite_get'))
