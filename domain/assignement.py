# -*- encoding: utf-8 -*-
from datetime import timedelta
from collections import defaultdict

import models


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
