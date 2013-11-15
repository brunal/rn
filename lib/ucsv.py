# -*- encoding: utf-8 -*-
"""
This module provides a drop-in replacement for csv.writer that supports unicode.
It simply shadows built-in writer from _csv
"""
from csv import *
from _csv import writer as _writer


class writer():
    def __init__(self, *args, **kwargs):
        self.__w = _writer(*args, **kwargs)

    @classmethod
    def __rec_encode(cls, *args):
        if len(args) == 1 and isinstance(args[0], basestring):
            return args[0].encode('utf-8')
        try:
            return map(cls.__rec_encode, *args)
        except TypeError:
            return cls.__rec_encode(unicode(args))

    @property
    def dialect(self):
        return self.__w.dialect

    def writerow(self, *args):
        return self.__w.writerow(self.__rec_encode(*args))

    def writerows(self, *args):
        return self.__w.writerows(self.__rec_encode(*args))
