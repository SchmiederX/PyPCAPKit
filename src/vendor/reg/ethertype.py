# -*- coding: utf-8 -*-
"""Ethertype IEEE 802 Numbers"""

import collections
import csv
import re

from pcapkit.vendor.default import Vendor

__all__ = ['EtherType']


class EtherType(Vendor):
    """Ethertype IEEE 802 Numbers"""

    FLAG = 'isinstance(value, int) and 0x0000 <= value <= 0xFFFF'
    LINK = 'https://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers-1.csv'

    def count(self, data):
        reader = csv.reader(data)
        next(reader)  # header
        return collections.Counter(map(lambda item: item[4],  # pylint: disable=map-builtin-not-iterating
                                       filter(lambda item: len(item[1].split('-')) != 2, reader)))  # pylint: disable=filter-builtin-not-iterating

    def rename(self, name, code):  # pylint: disable=arguments-differ
        if self.record[name] > 1:
            name = f'{name} [0x{code}]'
        return name

    def process(self, data):
        reader = csv.reader(data)
        next(reader)  # header

        enum = list()
        miss = list()
        for item in reader:
            name = item[4]
            rfcs = item[5]

            temp = list()
            for rfc in filter(None, re.split(r'\[|\]', rfcs)):
                if 'RFC' in rfc:
                    temp.append(f'[{rfc[:3]} {rfc[3:]}]')
                else:
                    temp.append(f'[{rfc}]')
            desc = re.sub(r'( )( )*', ' ', f"# {''.join(temp)}".replace('\n', ' ')) if rfcs else ''

            try:
                code, _ = item[1], int(item[1], base=16)
                renm = re.sub(r'( )( )*', ' ', self.rename(name, code).replace('\n', ' '))

                pres = f'{self.NAME}[{renm!r}] = 0x{code}'
                sufs = re.sub(r'\r*\n', ' ', desc, re.MULTILINE)

                if len(pres) > 74:
                    sufs = f"\n{' '*80}{sufs}"

                enum.append(f'{pres.ljust(76)}{sufs}')
            except ValueError:
                start, stop = item[1].split('-')
                more = re.sub(r'\r*\n', ' ', desc, re.MULTILINE)

                miss.append(f'if 0x{start} <= value <= 0x{stop}:')
                if more:
                    miss.append(f'    {more}')
                miss.append(
                    f"    extend_enum(cls, '{name} [0x%s]' % hex(value)[2:].upper().zfill(4), value)")
                miss.append('    return cls(value)')
        return enum, miss


if __name__ == "__main__":
    EtherType()
