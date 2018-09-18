# -*- coding: utf-8 -*-


import collections
import csv
import os
import re

import requests


###############
# Defaults
###############


ROOT, FILE = os.path.split(os.path.abspath(__file__))

LINE = lambda NAME, DOCS, FLAG, ENUM, MISS: '''\
# -*- coding: utf-8 -*-


from aenum import IntEnum, extend_enum


class {}(IntEnum):
    """Enumeration class for {}."""
    _ignore_ = '{} _'
    {} = vars()

    # {}
    {}

    @staticmethod
    def get(key, default=-1):
        """Backport support for original codes."""
        if isinstance(key, int):
            return {}(key)
        if key not in {}._member_map_:
            extend_enum({}, key, default)
        return {}[key]

    @classmethod
    def _missing_(cls, value):
        """Lookup function used when value is not found."""
        if not ({}):
            raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        {}
        super()._missing_(value)
'''.format(NAME, NAME, NAME, NAME, DOCS, ENUM, NAME, NAME, NAME, NAME, FLAG, MISS)


###############
# Macros
###############


NAME = 'RT_TYPE'
DOCS = 'IPv6 Routing Types'
FLAG = 'isinstance(value, int) and 0 <= value <= 255'
LINK = 'https://www.iana.org/assignments/ipv6-parameters/ipv6-parameters-3.csv'


###############
# Processors
###############


page = requests.get(LINK)
data = page.text.strip().split('\r\n')

reader = csv.reader(data)
header = next(reader)
record = collections.Counter(map(lambda item: item[1],
    filter(lambda item: len(item[0].split('-')) != 2, reader)))

def rename(name, code, *, original):
    if record[name] > 1:
        return '{} [{}]'.format(name, code)
    return name

reader = csv.reader(data)
header = next(reader)

enum = list()
miss = list()
for item in reader:
    long = item[1]
    rfcs = item[2]

    split = long.split(' (')
    if len(split) == 2:
        name = re.sub(r'\[\d+\]', '', split[0]).strip()
        cmmt = ' {}'.format(split[1][:-1])
    else:
        name, cmmt = re.sub(r'\[\d+\]', '', long).strip(), ''

    temp = list()
    for rfc in filter(None, re.split(r'\[|\]', rfcs)):
        if 'RFC' in rfc:
            temp.append('[{} {}]'.format(rfc[:3], rfc[3:]))
        else:
            temp.append('[{}]'.format(rfc))
    lrfc = " {}".format(''.join(temp)) if rfcs else ''

    try:
        code = int(item[0])
        renm = rename(name, code, original=long)

        pres = "{}[{!r}] = {}".format(NAME, renm, code).ljust(76)
        sufs = "#{}{}".format(lrfc, cmmt) if lrfc or cmmt else ''

        enum.append('{}{}'.format(pres, sufs))
    except ValueError:
        start, stop = item[0].split('-')

        miss.append('if {} <= value <= {}:'.format(start, stop))
        if lrfc or cmmt:
            miss.append('    #{}{}'.format(lrfc, cmmt))
        miss.append("    extend_enum(cls, '{} [%d]' % value, value)".format(name))
        miss.append('    return cls(value)')


###############
# Defaults
###############


ENUM = '\n    '.join(map(lambda s: s.rstrip(), enum))
MISS = '\n        '.join(map(lambda s: s.rstrip(), miss))
with open(os.path.join(ROOT, '../_common/{}'.format(FILE)), 'w') as file:
    file.write(LINE(NAME, DOCS, FLAG, ENUM, MISS))
