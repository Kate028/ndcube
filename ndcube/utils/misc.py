import inspect
from functools import wraps

from astropy.wcs.wcsapi import BaseHighLevelWCS

from ndcube.extra_coords import ExtraCoords

__all__ = ['sanitise_wcs', 'unique_sorted']


def unique_sorted(iterable):
    """
    Return unique values in the order they are first encountered in the iterable.
    """
    lookup = set()  # a temporary lookup set
    return [ele for ele in iterable if ele not in lookup and lookup.add(ele) is None]


def sanitise_wcs(func):
    """
    A wrapper for NDCube methods to sanitise the wcs argument.

    This decorator is only designed to be used on methods of NDCube.

    It will find the wcs argument, keyword or positional and if it is None, set
    it to `self.wcs`, if it is a `.ExtraCoords` object then it will call the
    ``.wcs`` property on the `.ExtraCoords`. It will finally verify that the
    object passed is a HighLevelWCS object.
    """
    @wraps(func)
    def wcs_wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        params = sig.bind(*args, **kwargs)
        wcs = params.arguments.get('wcs', None)
        self = params.arguments['self']

        if wcs is None:
            wcs = self.wcs

        if isinstance(wcs, ExtraCoords):
            wcs = wcs.wcs

        if not isinstance(wcs, BaseHighLevelWCS):
            raise TypeError("wcs argument must be a High Level WCS object.")

        params.arguments['wcs'] = wcs

        return func(*params.args, **params.kwargs)

    return wcs_wrapper
