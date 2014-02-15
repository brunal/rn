# -*- encoding: utf-8 -*-
from datetime import timedelta
from collections import defaultdict

from flask import url_for
from flask_mail import Message

import models
from lib import mail, filters


class Stats(object):
    def __init__(self):
        activites = models.Activite.query.all()
        self.tot_help_time = sum((a.nombre_volontaires * (a.fin - a.debut) for a in activites), timedelta())
        self.slots = sum(a.nombre_volontaires for a in activites)
        self.vols = models.Volontaire.query.count()

    @property
    def avg_slot_length(self):
        return self.tot_help_time / self.slots

    @property
    def avg_help_time(self):
        return self.tot_help_time / self.vols

    def assign_values(self):
        # this could be done in 3 queries... I suck at SQLalchemy
        ass_by_person = defaultdict(timedelta)
        for ass in models.Assignement.query.all():
            ass_by_person[ass.volontaire] += ass.activite.fin - ass.activite.debut
        times = ass_by_person.values()
        return min(times), max(times), sum(times, timedelta()) / len(times)


full_message = u"""{custom_message}

Voici la liste des tâches qui te sont affectées :

{tasks}

Je t'invite à les consulter plus en détail (coordonnées du resposable,
fichiers de ressources, etc.) à l'adresse {url}. Tu peux également y
télécharger un CSV récapitulatif.
En cas de problème, contacter Joseph : vice-president.brn@cgenational.com"""


def pp_activities(acts):
    acts_str = []
    for a in acts:
        s = u"- le %s de %s à %s : %s à %s" % (filters.to_date(a.debut),
                filters.to_time(a.debut), filters.to_time(a.fin),
                a.nom, a.lieu)
        acts_str.append(s)
    return "\n".join(acts_str)


def send_final_mail(subject, message):
    sent = 0
    for vol in models.Volontaire.query.all():
        msg = Message(subject, recipients=[vol.user.email])
        msg.body = full_message.format(custom_message=message,
                                       tasks=pp_activities(vol.activites),
                                       url=url_for('views.activite.my_assignements', _external=True))
        mail.send(msg)
        sent += 1
    return sent
