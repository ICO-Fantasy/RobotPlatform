from typing import Union

from OCC.Core.Quantity import *


def getColor(r: int | tuple[int, int, int], g=0, b=0):
    if isinstance(r, tuple):
        r, g, b = r
    return Quantity_Color(r / float(255), g / float(255), b / float(255), Quantity_TOC_RGB)
