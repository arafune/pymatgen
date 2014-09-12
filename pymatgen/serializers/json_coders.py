"""
.. versionadded:: 1.9.0

This module implements the abstract base class for PMGSONable pymatgen objects,
i.e., objects that can be converted to a json representation. MSON stands for
materials json.

It also implements general JSON encoders and decoders for pymatgen. Only
supports pymatgen objects version >= 1.9.0.

Current support for all core objects that obey the as_dict/from_dict API,
including Site, PeriodicSite, Structure, Specie, Dos, Lattice, etc. and all
Entry and  all Transformations. Note that nested lists and dicts of these
objects are supported as well.

.. note::

    The decoder depends on finding a "@module" and "@class" key in the dict in
    order to decode the necessary python object. All as_dict() properties must
    therefore have the module name and class embedded. In general, the
    MontyEncoder will add these keys if they are not present, but for better
    long term stability, the easiest way is to add the following to any as_dict()
    property::

        d["@module"] = self.__class__.__module__
        d["@class"] = self.__class__.__name__

"""

from __future__ import division
import six

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "Apr 30, 2012"

import json

from abc import ABCMeta

from monty.io import zopen
from monty.json import MSONable, MontyEncoder, MontyDecoder, MSONError
from monty.dev import deprecated


class PMGSONable(six.with_metaclass(ABCMeta, MSONable)):
    """
    This is an abstract base class specifying an API for MSONable objects.
    MSON is Pymatgen JSON. Essentially, PMGSONable objects must
    implement an as_dict() method and a from_dict static method.
    """

    @property
    @deprecated(
        message="All to_dict properties have been deprecated. They will be "
                "removed from v3.1. Use the as_dict() method instead.")
    def to_dict(self):
        """
        A JSON serializable dict representation of an object.
        """
        return self.as_dict()

    @classmethod
    def from_dict(cls, d):
        """
        This implements a default from_dict method which supports all
        classes that simply saves all init arguments in a "init_args"
        key. Otherwise, the PMGSONable class must override this class method.
        """
        if "init_args" in d:
            return cls(**d['init_args'])
        raise MSONError("Invalid dict for default from_dict. Please "
                        "override from_dict for ".format(cls))


def json_pretty_dump(obj, filename):
    """
    Serialize obj as a JSON formatted stream to the given filename (
    pretty printing version)
    """
    with open(filename, "w") as fh:
        json.dump(obj, fh, indent=4, sort_keys=4)


def pmg_load(filename, **kwargs):
    """
    Loads a json file and deserialize it with MontyDecoder.

    Args:
        filename (str): Filename of file to open. Can be gzipped or bzipped.
        \*\*kwargs: Any of the keyword arguments supported by the json.load
            method.

    Returns:
        Deserialized pymatgen object. Note that these objects can be lists,
        dicts or otherwise nested pymatgen objects that support the as_dict()
        and from_dict PMGSONable protocol.
    """
    return json.load(zopen(filename), cls=MontyDecoder, **kwargs)


def pmg_dump(obj, filename, **kwargs):
    """
    Dump an object to a json file using MontyEncoder. Note that these
    objects can be lists, dicts or otherwise nested pymatgen objects that
    support the as_dict() and from_dict PMGSONable protocol.

    Args:
        obj (object): Object to dump.
        filename (str): Filename of file to open. Can be gzipped or bzipped.
        \*\*kwargs: Any of the keyword arguments supported by the json.load
            method.
    """
    return json.dump(obj, zopen(filename, "w"), cls=MontyEncoder, **kwargs)