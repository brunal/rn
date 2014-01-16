def init_app(app):
    filters = app.jinja_env.filters
    filters['date'] = to_date
    filters['time'] = to_time


def to_date(dt):
    return dt.strftime("%A (%d)")


def to_time(dt):
    return dt.strftime("%Hh%M")
