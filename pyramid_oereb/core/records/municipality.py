# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any


@dataclass
class MunicipalityRecord:
    """
    The base document class.

    Attributes:
        fosnr (int): The unique id bfs of the municipality.
        name (unicode): The zipcode for this address.
        published (bool): Is this municipality ready for publishing via server.
        geom (str or None): The geometry which is representing this municipality as a WKT.
    """
    fosnr: int
    name: str
    published: bool
    geom: Any = None
