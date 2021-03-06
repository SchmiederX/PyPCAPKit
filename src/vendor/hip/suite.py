# -*- coding: utf-8 -*-
"""HIP Suite IDs"""

from pcapkit.vendor.default import Vendor

__all__ = ['Suite']


class Suite(Vendor):
    """Suite IDs"""

    FLAG = 'isinstance(value, int) and 0 <= value <= 65535'
    LINK = 'https://www.iana.org/assignments/hip-parameters/hip-parameters-6.csv'


if __name__ == "__main__":
    Suite()
