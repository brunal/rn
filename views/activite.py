# -*- encoding: utf-8 -*-
"""
Vues d'activités pour ceux qui n'en sont pas responsable
"""
from flask import Blueprint, send_from_directory, abort, render_template
from flask.ext.login import login_required
from werkzeug import secure_filename

import upload
import models


bp = Blueprint(__name__, __name__, url_prefix='/activite/')


# Accès aux données des activités

@bp.route('')
@login_required
def list_activites():
    activites = models.Activite.query.all()
    return render_template('activites.html', activites=activites)


@bp.route('<int:activite_id>/')
@login_required
def activite(activite_id):
    activite = models.Activite.query.get(activite_id) or abort(404)
    ressources = upload.list_files(activite.responsable.user.email)
    return render_template('activite.html', activite=activite, ressources=ressources)


@bp.route('<int:activite_id>/<filename>')
@login_required
def get_asset(activite_id, filename):
    activite = models.Activite.query.get(activite_id) or abort(404)
    folder = upload.get_folder(activite.responsable.user.email)
    return send_from_directory(folder, secure_filename(filename))
