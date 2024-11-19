#!/usr/bin/env python

__doc__ = """
Contains dotdictify class.
"""


class dotdictify(dict):
    """
    life = {
        'bigBang': {
            'stars': {
                'planets': {}
            }
       }
    }

    >>> life = dotdictify(life)
    >>> print life.bigBang.stars.planets
    >>> life.bigBang.stars.planets.earth = {'singleCellLife': 1}
    >>> print life.bigBang.stars.planets
    >>> print life.bigBang.stars.planets.earth.singleCellLife
    """

    marker = object()

    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError("expected dict")

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, dotdictify):
            value = dotdictify(value)
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        found = self.get(key, dotdictify.marker)
        if found is dotdictify.marker:
            found = dotdictify()
            dict.__setitem__(self, key, found)
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__
