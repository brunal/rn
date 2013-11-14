# -*- encoding: utf-8 -*-
"""
Vues d'activités pour ceux qui n'en sont pas responsable
"""
from flask import Blueprint, send_from_directory, abort, render_template
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename

import upload
from models import Activite


bp = Blueprint(__name__, __name__, url_prefix='/activite/')


# Accès aux données des activités

@bp.route('')
@login_required
def list_activites():
    u = current_user.user
    if u.brn or u.responsable:
        activites = Activite.query.all()
    elif u.volontaire:
        activites = u.volontaire.activites
    activites.sort(key=lambda a: a.debut)
    return render_template('activites.html', activites=activites)


def can_view_activite(user, id):
    if user.brn or user.responsable:
        return True
    if user.volontaire:
        return user.volontaire.is_affected_to(id)


def get_authorized_activite(a_id):
    can_view_activite(current_user.user, a_id) or abort(401)
    return Activite.query.get(a_id) or abort(404)


@bp.route('<int:activite_id>/')
@login_required
def activite(activite_id):
    activite = get_authorized_activite(activite_id)
    ressources = upload.list_files(activite.id)
    return render_template('activite.html', activite=activite, ressources=ressources)


@bp.route('<int:activite_id>/<filename>')
@login_required
def get_asset(activite_id, filename):
    activite = get_authorized_activite(activite_id)
    folder = upload.get_folder(activite.id)
    return send_from_directory(folder, secure_filename(filename))
