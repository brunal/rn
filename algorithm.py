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
    planning : models.Planning list
    """

    def __init__(self, tasks, people, planning):
        planning_s = sorted(planning, key=lambda p: p.debut)
        tasks_s = sorted(tasks, key=lambda p: p.debut)
        self.plans = Plan.make_plans(planning_s, tasks_s)
        self.people = people

    def solve():
        """
        Returns
        -------
        models.Affectation list
        """
        return []


class Plan(object):
    """Represent a segment of a planning.

    Has a start time and possible extits to other plans, at different times
    From a root plan starts a tree which represents possible plannings

    Parameters
    ----------
    start_time : datetime
    """
    def __init__(self, what):
        self.what = what
        self.exits = []

    def add_exit(self, when, plan):
        self.exits.append((when, plan))

    @classmethod
    def make_plans(cls, planning, tasks):
        """Build a possible planning

        Each task can or cannot be taken, and overrides a planned activity
        from planning

        Parameters
        ----------
        planning : models.Planning list
        tasks : models.Task list

        Returns
        -------
        plans : Plan list
        """
        i = j = 0
        i_max, j_max = len(planning), len(tasks)

        while i < i_max and j < j_max:
            if planning[i] <= planning[j]:
                # push next planned activity
                nex = planning[i]
                i += 1
            else:
                nex = tasks[j]
                j += 1

            p = Plan(nex)
            plans = cls.make_plans(planning[i:], tasks[j:])
            map(p.add_exit, plans)
        return p
