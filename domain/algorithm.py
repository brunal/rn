# -*- encoding: utf-8 -*-
import logging as log


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

    # DO ASSIGNEMENTS HERE

    CONTEXT.pop()
    # cannot import at module level (recursive imports)
    from views import assignements
    assignements.background_script = False
    logging.info(u"Fin de la procédure d'affectation")
    return True
