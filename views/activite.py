# -*- encoding: utf-8 -*-
"""
Vues d'activités
"""
from flask import Blueprint, send_from_directory, abort, render_template, url_for
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename

from login import requires_roles
from models import Activite, Volontaire, Responsable, BRN
from domain.activites import to_csv, csv_response
from lib import upload


bp = Blueprint(__name__, __name__, url_prefix='/activite/')


def asort(acts):
    return sorted(acts, key=lambda a: a.debut)


@bp.route('')
@requires_roles(Volontaire)
def my_assignements():
    acts = asort(current_user.user.volontaire.activites)
    return render_template('activites.html', activites=acts,
                           csv_version=url_for('.my_assignements_csv'),
                           acts_title="Tes affectations")


@bp.route('csv')
@requires_roles(Volontaire)
def my_assignements_csv():
    acts = asort(current_user.user.volontaire.activites)
    return csv_response(to_csv(acts), "mes_affectations")


@bp.route('miennes')
@requires_roles(Responsable)
def my_activities():
    activites = asort(current_user.user.responsable.activites)
    return render_template('responsable_activites.html', activites=activites,
                           csv_version=url_for('.my_activities_csv'))


@bp.route('miennes.csv')
@requires_roles(Responsable)
def my_activities_csv():
    activites = asort(current_user.user.responsable.activites)
    return csv_response(to_csv(activites), "mes_activites")


@bp.route('toutes')
@requires_roles(Responsable, BRN)
def all_activities():
    activites = asort(Activite.query.all())
    return render_template("activites.html", activites=activites,
                           csv_version=url_for('.all_activities_csv'),
                           acts_title=u"Activités de la RN ayant besoin de volontaires")


@bp.route('toutes.csv')
@requires_roles(Responsable, BRN)
def all_activities_csv():
    activites = asort(Activite.query.all())
    return csv_response(to_csv(activites), "toutes_activites")


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
