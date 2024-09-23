"""圆弧有关的计算"""
import numpy as np
import numpy.typing as npt

from mathTools.Vectors import calculateAngleBetweenVectors


def calculateArcAngle(
    center: npt.NDArray[np.float64],
    p1: npt.NDArray[np.float64],
    p2: npt.NDArray[np.float64],
    p3: npt.NDArray[np.float64],
) -> float:
    """计算圆弧的角度 (rad)"""
    vector1 = p1 - center
    vector2 = p2 - center
    vector3 = p3 - center

    angle1 = calculateAngleBetweenVectors(vector1, vector2)
    angle2 = calculateAngleBetweenVectors(vector2, vector3)
    angle = angle2 + angle1
    # 确保角度在 90 到 180 度之间
    if angle < np.pi:
        angle = np.pi - angle

    return angle
