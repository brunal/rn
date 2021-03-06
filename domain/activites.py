# -*- encoding: utf-8 -*-
from cStringIO import StringIO

from flask import Response

from lib import ucsv
from lib.filters import to_date, to_time


def to_csv(activites):
    csv_activites = StringIO()
    w = ucsv.writer(csv_activites)
    # headers
    w.writerow(['Jour', u'Début', 'Fin', 'Nom', 'Lieu', 'Responsable', 'Email', 'Description'])
    for a in activites:
        w.writerow([to_date(a.debut), to_time(a.debut), to_time(a.fin),
                    a.nom, a.lieu,
                    a.responsable.user.name, a.responsable.user.email,
                    a.description])

    return csv_activites.getvalue()


def csv_response(csv, filename):
    if not filename.endswith(".csv"):
        filename += ".csv"
    return Response(csv, content_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment;filename=%s" % filename})
