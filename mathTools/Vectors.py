"""向量有关的计算"""
import numpy as np
import numpy.typing as npt


def calculateAngleBetweenVectors(vector1: npt.NDArray[np.float64], vector2: npt.NDArray[np.float64], degree=False) -> float:
    """两向量夹角"""
    dotProduct = np.dot(vector1, vector2)
    normVector1 = np.linalg.norm(vector1)
    normVector2 = np.linalg.norm(vector2)

    cosTheta = dotProduct / (normVector1 * normVector2)

    # 使用 arccos 函数计算角度（弧度）
    angleRad: float = np.arccos(cosTheta)

    if degree:
        # 将弧度转换为角度
        angleDeg = np.degrees(angleRad)

        return angleDeg
    return angleRad
