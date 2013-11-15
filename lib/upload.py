"""
Assets-uploading & retrieval related functions
"""
from werkzeug import secure_filename
from os import makedirs, path, listdir, remove


class config(object):
    ALLOWED_EXTENSIONS = []
    UPLOAD_FOLDER = ""


def init_app(app):
    config.ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
    config.UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


def get_folder(owner_id):
    folder = secure_filename(str(owner_id))
    folder = path.join(config.UPLOAD_FOLDER, folder)
    if not path.exists(folder):
        makedirs(folder)
    return folder


def upload_files(owner_id, files):
    """
    Upload a list of files. Each must have an attribute 'filename' and method
    save(path).
    :param owner_id: identifier for the files' owner
    :return: (list of successful filenames, list of illegal filenames)
    """
    folder = get_folder(owner_id)

    successes, failures = [], []
    for f in files:
        if allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(path.join(folder, filename))
            successes.append(filename)
        else:
            failures.append(f.filename)

    return successes, failures


def list_files(owner_id):
    return listdir(get_folder(owner_id))


def delete_file(owner_id, filename):
    try:
        filepath = path.join(get_folder(owner_id), secure_filename(filename))
        remove(filepath)
        return True
    except Exception as e:
        return e.message
