import numpy as np
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from OCC.Core.gp import *


def add_numbers(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now()
    print(now)  # Output: 2023-07-11 16:25:00+01:00

# end main
