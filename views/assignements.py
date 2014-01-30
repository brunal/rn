# -*- encoding: utf-8 -*-
"""Affectation pags"""
from datetime import datetime, timedelta
from threading import Thread
import logging

from flask import Blueprint, render_template, url_for, flash, redirect
from flask_mail import Message

import models
import forms
from login import requires_roles
from lib import mail
from lib.filters import to_time
from domain import algorithm, assignement


bp = Blueprint(__name__, __name__, url_prefix='/affectations/')


@bp.route('')
@requires_roles(models.BRN)
def status():
    # misc. stats
    stats = assignement.Stats()
    assign_auto = models.Assignement.auto().count()
    assign_manual = models.Assignement.manual().count()

    return render_template('assignements/status.html',
                           activites_count=models.Activite.query.count(),
                           stats=stats,
                           assign_auto=assign_auto,
                           assign_manual=assign_manual)


def warn_for_cancellation(assignement, unav):
    raw_txt = u"{} n'est plus affecté(e) à '{}' ({}): il/elle est indisponible à ce moment (%s entre %s et %s)."
    activite_url = url_for('views.responsable.activite_get', a_id=assignement.activite.id, _external=True)
    txt = raw_txt.format(assignement.volontaire.user.name,
                         assignement.activite.nom,
                         activite_url,
                         unav.reason, to_time(unav.begin), to_time(unav.end))

    recipient = assignement.activite.responsable.user.email
    msg = Message(u'[RN] Affectation manuelle supprimée',
                  recipients=[recipient])
    msg.body = txt
    mail.send(msg)

    flash(u"Envoi d'un email au responsable %s" % recipient)
    return True


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
            warn_for_cancellation(assignement, u)
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


background_script = False


@bp.route('automatique')
@requires_roles(models.BRN)
def automatic():
    activites = models.Activite.query.all()
    slots = sum(a.nombre_volontaires for a in activites)
    assign_manual = models.Assignement.manual().count()
    assign_auto = models.Assignement.auto().count()

    try:
        with open(algorithm.OUT_FILE, 'rb') as f:
            content = f.read().decode('utf8')
    except IOError:
        logging.exception("Cannot read file %s", algorithm.OUT_FILE)
        content = None

    return render_template('assignements/auto.html',
                           slots=slots - assign_manual - assign_auto,
                           assigned_auto=assign_auto,
                           affectation_running=background_script,
                           algo_output=content)


@bp.route('supprimer-affectations-auto')
@requires_roles(models.BRN)
def delete_assignements():
    delete_count = len(map(models.db.session.delete, models.Assignement.auto()))
    models.db.session.commit()
    flash(u'%s affectations supprimées' % delete_count)
    logging.info("Deleted %s automatic assignements", delete_count)
    return redirect(url_for('.automatic'))


@bp.route('commencer-affectations')
@requires_roles(models.BRN)
def start_assigning():
    global background_script
    background_script = True
    Thread(target=algorithm.start).start()
    flash(u"Une procédure a été lancée")
    flash(u"Viens ici te tenir au courant de l'avancement")
    flash(u"Le BRN recevra un mail à la fin de la procédure")
    logging.info("Launched assignement algorithm")
    return redirect(url_for('.automatic'))
