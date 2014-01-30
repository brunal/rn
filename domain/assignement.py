# -*- encoding: utf-8 -*-
import models
from datetime import timedelta


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
