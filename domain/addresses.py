# -*- encoding: utf-8 -*-
from datetime import timedelta
import logging
import urllib2
import json
from math import sin, cos, sqrt, atan2


class TravelAgent(object):

    def clean(self, addr):
        return addr.replace('-', ' ') \
                   .lower() \
                   .replace(u'è', 'e') \
                   .replace(u'à', 'a') \
                   .replace(u'é', 'e')

    def get_time_between(self, addr1, addr2):
        return NotImplementedError()


class Naive(TravelAgent):
    _closeness_hacks = [("Assas", 10), ("75006", 15), ("Montmartre", 15)]

    def get_time_between(self, addr1, addr2):

        if addr1 == addr2:
            return timedelta(0)
        else:
            for k, d in self._closeness_hacks:
                if k in addr1 and k in addr2:
                    # we know the travel time
                    return timedelta(minutes=d)
            return timedelta(30)


class Geocoding(TravelAgent):
    _memory = {}
    R = 6373.0
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={address}, France&sensor=false"

    def position(self, address):
        if address in self._memory:
            return self._memory[address]

        url = self.url.format(address=self.clean(address))
        content = urllib2.urlopen(url).read()

        json_response = json.loads(content)
        if json_response["status"] != "OK" or not json_response["results"]:
            logging.warning(u"Problem getting position of address %s", address)

        result = json_response["results"][0]["geometry"]["location"]
        logging.info("%s is at %s", address, result)
        self._memory[address] = result
        return result

    def get_distance_between(self, addr1, addr2):
        lat1, lon1 = self.position(addr1)
        lat2, lon2 = self.position(addr2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2)) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return self.R * c

    def get_time_between(self, addr1, addr2):
        kms = self.get_distance_between(addr1, addr2)
        #8mk/h, min 3 min, max 40 min
        minutes = kms * 7.5
        if minutes < 3:
            minutes = 3
        elif minutes > 40:
            minutes = 40
        return timedelta(minutes=minutes)


class Knowledge(TravelAgent):
    def __init__(self):
        self.cols = ["saint germain", "sevres", "chimie paris", "champs",
                     "sem", "ulm", "sorbonne", "jacques"]
        self.rows = ["saint germain", "mep", "lazariste",
                     "nd des champs", "sem", "st ignace"]

        self.values = [[0, 9, 19, 21, 14, 22, 13, 18],
                       [13, 3, 26, 13, 27, 27, 21, 22],
                       [16, 4, 27, 12, 29, 28, 23, 23],
                       [21, 13, 20, 0, 25, 19, 21, 17],
                       [14, 28, 7, 25, 0, 9, 7, 10],
                       [11, 0, 23, 12, 25, 24, 19, 20]]
        self.naive = Naive()

    def get_time_between(self, addr1, addr2):
        addr1 = self.clean(addr1)
        addr2 = self.clean(addr2)

        length = self._get_time_between(addr1, addr2)
        if length is None:
            length = self._get_time_between(addr2, addr1)
            if length is None:
                logging.info("Pas d'info pour aller de %a à %a -> pifomètre",
                             addr1, addr2)
                return self.naive.get_time_between(addr1, addr2)
        return length

    def _get_time_between(self, addr1, addr2):
        for i, name in enumerate(self.cols):
            if name in addr1:
                for j, name2 in enumerate(self.rows):
                    if name2 in addr2:
                        return timedelta(minutes=self.values[j][i])
        return None


DEFAULT_AGENT = Knowledge
