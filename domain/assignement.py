"""
Here lies the heart of the application: computation of affectation for everyone

Idée générale de l'algorithme :
    - un ensemble de personnes et leurs disponibilités
    - un ensemble de tâches à répartir entre les personnes
    - on assigne : pour chaque tâche on choisit un volontaire libre, en optimisant
    les paramètres secondaires :
        - pas bcp de tâches encore
        - bon sexe
        - temps libre de la personne
        - etc.
    - si personne de libre on prend quelqu'un qui a raté peu de choses avec les
    mêmes critères secondaires

Complexité : #personnes * #taches
"""
import logging
from datetime import timedelta


class Task(object):
    def __init__(self):
        pass


class State(object):
    def __init__(self, tasks, slots):
        self.tasks = tasks
        self.slots = slots


class Affector(object):
    """
    Parameters
    ----------
    tasks : models.Activite list
    people : models.Volontaire list
    """

    def __init__(self, tasks, people):
        self.tasks = sorted(tasks, key=lambda p: p.debut)
        self.people = people
        self.date_to_events, \
            self.people_to_date, \
            self.date_to_people = self.build_map()

        self.avg_service_time = sum(t.fin - t.debut for t in tasks) / len(people)
        logging.info("Temps de service moyen = %s", self.avg_service_time)

    @classmethod
    def overlaps(cls, b1, e1, b2, e2):
        return b1 <= b2 <= e1 or b2 <= b1 <= e2

    @classmethod
    def spans_between(cls, beginning, end):
        return [beginning + n * span for n in range((end - beginning) / span + 1)]

    def build_map(self):
        """Build 2 dicts of availability

        Returns
        -------
        avail_what : {when: what}
        avail_when, : {who: when}
        avail_who : {when: who}
        """
        beginning = min(t.debut for t in self.tasks)
        end = max(t.fin for t in self.tasks)
        # split in 5-minutes time spans
        self.span = timedelta(minutes=5)
        times = [beginning + n * span for n in range((end - beginning) / span + 1)]
        avail_what = {}
        avail_who = {}
        for t in times:
            avail_what[t] = self._happening_at(t)

        for p in self.people:
            avail_when[p] = self._free_when(p, times)

        avail_who = self._reverse_dict(avail_whenà

        return avail_what, avail_when, avail_who

    def _happening_at(self, time):
        return set(t for t in self.tasks
                   if t.debut <= time <= t.fin)

    def _free_when(self, person, times):
        # load reserved time
        raise NotImplementedError()
        unav = [(u.beginning, u.end) for u in person.unavailabilities]
        acts = [(a.debut, a.fin) for a in person.manual_assignements]

        spans_taken = sorted(unav + acts, key=lambda (b, e): b)
        times = list(times)
        taken = []
        for b, e in spans_taken:
            taken.append(b + n * span for n

    def solve(self):
        """
        Returns
        -------
        models.Affectation list
        """
        for when, who in sorted(self.date_to_people.iteritems(),
                                key=lambda (d, p): len(p), reverse=True):
            # time with the fewest available people
            events = self.date_to_events[when]
            if sum(e.needed() for e in event) > len(who):
                logging.warning(u"Pas assez de monde à l'heure %s" % when)
                

        #self.date_to_events, \
        #    self.people_to_date, \
        #    self.date_to_people = self.build_map()
