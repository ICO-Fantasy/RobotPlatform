from typing import Annotated, Literal, TypeVar

import numpy as np
from numpy.typing import ArrayLike, NDArray

Radian = Annotated[float, "radians"]
TransformMatrix_4x4 = Annotated[NDArray[np.float_], Literal[4, 4]]
TransformMatrix_4x3 = Annotated[NDArray[np.float_], Literal[4, 3]]
