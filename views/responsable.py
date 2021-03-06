# -*- encoding: utf-8 -*-
"""
Vues pour les responsables : gestion d'un pôle
"""
from datetime import datetime, timedelta

from flask import Blueprint, Response, render_template, redirect, url_for, request, flash, abort
from flask.ext.login import current_user

import forms
import models
from domain.activites import to_csv
from login import requires_roles
from lib import upload


bp = Blueprint(__name__, __name__, url_prefix='/responsable/')


# Gestion de l'activité, réservée à son responsable

def get_activite(id):
    activite = models.Activite.query.get(id) or abort(404)
    if not current_user.user.brn and \
       activite.responsable != current_user.user.responsable:
        abort(401)
    return activite


@bp.route('csv')
@requires_roles(models.Responsable)
def csv_activites():
    csv = to_csv(current_user.user.role.activites)
    return Response(csv, content_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment;filename=mes_activites.csv"})


@bp.route('')
@requires_roles(models.Responsable)
def list_activites():
    activites = sorted(current_user.user.role.activites, key=lambda a: a.debut)
    return render_template('responsable_activites.html', activites=activites)


def vols_choices_for(a_id):
    """Returns available + already affected volontaires"""
    a = models.Activite.query.get(a_id)
    return [(v.id, v.user.name)
            for v in a.assignees + a.get_available_volontaires()]


@bp.route('nouvelle/')
@bp.route('<int:a_id>/')
@requires_roles(models.Responsable, models.BRN)
def activite_get(a_id=None, form=None):
    if a_id is None:
        form = form or forms.Activite()
        return render_template('config_activite.html', form=form)

    activite = get_activite(a_id)
    form = form or forms.Activite(obj=activite)
    if activite.debut:
        form.jour.data = (activite.debut.date() - forms.JEUDI).days

    assign = forms.ManualActiviteAssignement(people=[a.volontaire.id
                                                     for a in activite.assignements])
    assign.people.choices = vols_choices_for(a_id)

    return render_template('config_activite.html', form=form, a_id=activite.id,
                           files=upload.list_files(activite.id),
                           extensions=upload.config.ALLOWED_EXTENSIONS,
                           assignements=activite.assignements,
                           assign=assign)


@bp.route('nouvelle/', methods=['POST'])
@bp.route('<int:a_id>/', methods=['POST'])
@requires_roles(models.Responsable, models.BRN)
def activite_post(a_id=None):
    form = forms.Activite(request.form)
    if not form.validate():
        return activite_get(a_id, form=form)

    if a_id is None:
        if current_user.user.brn:
            # cannot create new activity
            flash(u'Il est impossible pour un membre du BRN de créer une activité')
            redirect(url_for('views.activite.list_activites'))

        activite = models.Activite()
        activite.responsable = current_user.user.role
        models.db.session.add(activite)
        flash(u'Activité créée')
    else:
        activite = get_activite(a_id)
        flash(u'Activité mise à jour')

    form.populate_obj(activite)

    jour = forms.JEUDI + timedelta(form.jour.data)
    activite.debut = datetime.combine(jour, form.debut.data)
    activite.fin = datetime.combine(jour, form.fin.data)

    models.db.session.commit()

    return redirect(url_for('.activite_get', a_id=activite.id))


@bp.route('<int:a_id>/assign', methods=['POST'])
@requires_roles(models.Responsable, models.BRN)
def assign(a_id):
    assign = forms.ManualActiviteAssignement(request.form)
    assign.people.choices = vols_choices_for(a_id)
    if not assign.validate():
        return activite_get()

    # delete the ones that have changed
    prev_assign_dict = {a.volontaire_id: a
                        for a in get_activite(a_id).assignements}

    for vid in assign.people.data:
        if vid in prev_assign_dict:
            # nothing to do
            del prev_assign_dict[vid]
            continue

        # add it
        a = models.Assignement()
        a.activite_id = a_id
        a.volontaire_id = vid
        a.source = a.MANUAL
        models.db.session.add(a)

        vname = models.Volontaire.query.get(vid).user.name
        flash(u"%s affecté à la tâche" % vname)

    # delete previous ones
    for p_a in prev_assign_dict.values():
        flash(u"%s enlevé de la tâche" % p_a.volontaire.user.name)
        models.db.session.delete(p_a)

    models.db.session.commit()

    return redirect(url_for('.activite_get', a_id=a_id))


@bp.route('<int:a_id>/upload', methods=['POST'])
@requires_roles(models.Responsable)
def upload_page(a_id):
    activite = get_activite(a_id)
    files = request.files.getlist('files')
    successes, failures = upload.upload_files(activite.id, files)
    if successes:
        flash(u'Succès : {}'.format(', '.join(successes)))
    if failures:
        flash(u'Echecs : {}'.format(', '.join(failures)))
    return redirect(url_for('.activite_get', a_id=activite.id))


@bp.route('<int:a_id>/delete/')
@requires_roles(models.Responsable)
def delete_activite(a_id):
    activite = get_activite(a_id)
    map(models.db.session.delete, activite.assignements)
    models.db.session.delete(activite)
    models.db.session.commit()
    flash(u'Activité supprimée')
    return redirect(url_for('.list_activites'))


@bp.route('<int:a_id>/delete/<filename>')
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
