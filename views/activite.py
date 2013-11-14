# -*- encoding: utf-8 -*-
"""
Vues d'activités pour ceux qui n'en sont pas responsable
"""
from cStringIO import StringIO
import ucsv

from flask import Blueprint, Response, send_from_directory, abort, render_template
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename

import upload
from models import Activite
from filters import to_date, to_time


bp = Blueprint(__name__, __name__, url_prefix='/activite/')


# Accès aux données des activités

def activites():
    u = current_user.user
    if u.brn or u.responsable:
        activites = Activite.query.all()
    elif u.volontaire:
        activites = u.volontaire.activites
    return sorted(activites, key=lambda a: a.debut)


@bp.route('')
@login_required
def list_activites():
    return render_template('activites.html', activites=activites())


@bp.route('csv')
@login_required
def csv_activites():
    acts = activites()
    csv_activites = StringIO()
    w = ucsv.writer(csv_activites)
    # headers
    w.writerow(['Jour', u'Début', 'Fin', 'Nom', 'Lieu', 'Responsable', 'Email'])
    for a in acts:
        w.writerow([to_date(a.debut), to_time(a.debut), to_time(a.fin),
                    a.nom, a.lieu,
                    a.responsable.user.name, a.responsable.user.email])

    return Response(csv_activites.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=planning.csv"})


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
