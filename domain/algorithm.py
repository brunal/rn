# -*- encoding: utf-8 -*-
"""
Here lies the heart of the application: computation of assignements for everyone
"""
import logging as log
import models
from datetime import timedelta

from domain.assignement import Stats

logging = log.getLogger('rn.domain.algorithm')
logging.setLevel(log.DEBUG)

OUT_FILE = None
CONTEXT = None


def init_app(app):
    global OUT_FILE
    global CONTEXT

    OUT_FILE = app.config['ALGO_OUT_FILE']

    to_file = log.FileHandler(OUT_FILE)
    to_file.setLevel(log.DEBUG)
    logging.addHandler(to_file)

    CONTEXT = app.test_request_context()


def start():
    # erase log file
    open(OUT_FILE, 'w').close()
    logging.info(u"Démarrage de la procédure d'affectation")

    # we need the app with a context for db access...
    CONTEXT.push()

    try:
        Assignator().solve()
    except:
        logging.exception("Probleme lors de l'affectation")
        return False
    finally:
        CONTEXT.pop()
        # cannot import at module level (recursive imports)
        from views import assignements
        assignements.background_script = False
        logging.info(u"Fin de la procédure d'affectation")

    return True


class Assignator(object):
    def __init__(self):
        self.stats = Stats()

    def get_tasks(self):
        return iter(models.Activite.most_in_need_of_help())

    def solve(self):
        impossible = set([None])
        while True:
            tasks = self.get_tasks()
            if not tasks:
                logging.info(u"Toutes les tâches ont été remplies !")
                return

            t = None
            try:
                while t in impossible:
                    t = next(tasks)
            except StopIteration:
                logging.info("Impossible de trouver des volontaires pour les activités restantes")
                return

            # try to assign someone to t
            potential_helpers = t.get_available_volontaires()
            if not potential_helpers:
                logging.info(u"Personne n'est disponible pour '%s': elle restera bloquée à %s/%s",
                             t.nom, t.nombre_volontaires, len(t.assignees))
                impossible.add(t)
                continue

            if len(potential_helpers) < t.nombre_volontaires:
                logging.warning("Il sera impossible de remplir '%s': il faut %s personnes, il y en a %s dispos au max",
                                t.nom, t.nombre_volontaires, len(potential_helpers))

            helper = self.find_best_match(potential_helpers, t)
            if helper is None:
                logging.info(u"Personne ne peut faire '%s' (problème de trajet ?)")
                impossible.add(t)
                continue

            logging.info(u"%s assigné à '%s'", helper.user.name, t.nom)
            self.push_assignement(helper, t)

    def find_best_match(self, helpers, task):
        # soft constraints
        for f in [self._on_work_time, self._on_gender]:
            helpers_ = f(helpers, task)
            if len(helpers_) == 1:
                return helpers_[0]
            elif helpers_:
                helpers = helpers_

        # hard constraints
        for f in [self._on_work_time_hard, self._on_grouping]:
            helpers = self._on_grouping(helpers, task)
            if not helpers:
                return None

        # take the one who works the least
        return min(helpers, key=lambda h: h.help_time)

    def _on_work_time(self, helpers, task):
        helpers = filter(lambda h: h.help_time < self.stats.avg_help_time, helpers)
        if not helpers:
            logging.debug("Tout le monde travaille trop pour faire '%s'!", task.nom)
        return helpers

    def _on_work_time_hard(self, helpers, task):
        helpers = filter(lambda h: h.help_time < 1.5 * self.stats.avg_help_time, helpers)
        if not helpers:
            logging.debug("Tout le monde travaille BEAUCOUP trop pour faire '%s'!", task.nom)
        return helpers

    def _on_gender(self, helpers, task):
        if task.get_sexe() is models.SexeActivite.Aucune:
            return helpers

        # filter on gender
        genders = [ass.user.sexe for ass in task.assignees
                   if ass.user.sexe is not None]
        if len(set(genders)) <= 1:
            # no choice -> pointless
            return helpers

        # -0.5 per M, +0.5 per F
        mean_gender = sum(g - 1.5 for g in genders)
        goal = task.sexe - 1.5
        if mean_gender / goal > 0.5:
            # at least 75% of asked gender
            return helpers

        # pick people with the requested gender
        return filter(lambda h: h.user.sexe == task.sexe, helpers)

    def _on_grouping(self, helpers, task):
        # who has a task nearby?
        tiers = {0: [], 1: [], 2: []}

        for h in helpers:
            # task too near?
            acts = h.activites
            # check before
            score1 = 0
            before = filter(lambda a: a.fin < task.debut, acts)
            if before:
                previous = max(before, key=lambda a: a.fin)
                score1 = self._rate_closeness(previous, task)
                if score1 == -1:
                    continue

            # check after
            score2 = 0
            after = filter(lambda a: a.debut > task.fin, acts)
            if after:
                next = min(after, key=lambda a: a.debut)
                score2 = self._rate_closeness(task, next)
                if score2 == -1:
                    continue

            tiers[score1 + score2].append(h)

        # return best non-empty tier
        for tier in [2, 1, 0]:
            if tiers[tier]:
                return tiers[tier]
        return []

    def _rate_closeness(self, t1, t2):
        """
        -1 = impossible
        0 = ok
        1 = cool
        """
        if (t2.debut - t1.fin) < timedelta(minutes=30) and \
           t2.lieu != t1.lieu:
            # not enough time!
            logging.debug(u"On ne peut pas aller de %s à %s suffisamment rapidement",
                          t1.lieu, t2.lieu)
            return -1
        elif (t2.debut - t1.fin) < timedelta(minutes=180):
            return 1
        else:
            return 0

    def push_assignement(self, helper, task):
        a = models.Assignement()
        a.volontaire = helper
        a.activite = task
        a.source = a.AUTOMATIC
        models.db.session.add(a)
        models.db.session.commit()
