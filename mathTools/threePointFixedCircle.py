"""三点定圆"""
import logging

import numpy as np
import numpy.typing as npt

from mathTools.Arc import calculateArcAngle

log = logging.getLogger(__name__)


def threePointFixedCircle(
    point1: list[float] | list[list],
    point2: list[float] = [0, 0, 0],
    point3: list[float] = [0, 0, 0],
    linear_tolerance=1e-6,
) -> tuple[npt.NDArray[np.float64], float, float]:
    """
    三点定圆

    Return
    ------
    circle_center, radius, angle
    """
    if isinstance(point1[0], tuple):
        point1, point2, point3 = point1  # type: ignore
    from numpy.linalg import det

    p1 = np.array(point1)
    p2 = np.array(point2)
    p3 = np.array(point3)
    num1 = len(p1)
    num2 = len(p2)
    num3 = len(p3)

    # 输入检查
    if (num1 == num2) and (num2 == num3):
        if num1 == 2:
            p1 = np.append(p1, 0)
            p2 = np.append(p2, 0)
            p3 = np.append(p3, 0)
        elif num1 != 3:
            log.warning("\t仅支持二维或三维坐标输入")
    else:
        log.warning("\t输入坐标的维数不一致")

    # 共线检查
    temp01 = p1 - p2  # type: ignore
    temp02 = p3 - p2  # type: ignore
    temp03 = np.cross(temp01, temp02)
    # 计算两个向量（向量数组）的叉乘。叉乘返回的数组既垂直于a，又垂直于b。
    # 如果a,b是向量数组，则向量在最后一维定义。该维度可以为2，也可以为3. 为2的时候会自动将第三个分量视作0补充进去计算。
    temp = (temp03 @ temp03) / (temp01 @ temp01) / (temp02 @ temp02)  # @装饰器的格式来写的目的就是为了书写简单方便
    # temp03 @ temp03中的@ 含义是数组中每个元素的平方之和
    if temp < linear_tolerance:
        log.warning("\t三点共线, 无法确定圆")

    temp1 = np.vstack((p1, p2, p3))  # 行拼接
    temp2 = np.ones(3).reshape(3, 1)  # 以a行b列的数组形式显示
    mat1 = np.hstack((temp1, temp2))  # size = 3x4

    m = +det(mat1[:, 1:])
    n = -det(np.delete(mat1, 1, axis=1))  # axis=1相对于把每一行当做列来排列
    p = +det(np.delete(mat1, 2, axis=1))
    q = -det(temp1)

    temp3 = np.array([p1 @ p1, p2 @ p2, p3 @ p3]).reshape(3, 1)  # type: ignore
    temp4 = np.hstack((temp3, mat1))
    # 使用 stack，可以将一个列表转换为一个numpy数组，当axis=0的时候，和 使用 np.array() 没有什么区别，
    # 但是当 axis=1的时候，那么就是对每一行进行在列方向上进行运算，也就是列方向结合，
    # 此时矩阵的维度也从（2,3）变成了（3,2）
    # hstack(tup) ，参数tup可以是元组，列表，或者numpy数组，返回结果为numpy的数组
    temp5 = np.array([2 * q, -m, -n, -p, 0])
    mat2 = np.vstack((temp4, temp5))  # size = 4x5

    A = +det(mat2[:, 1:])
    B = -det(np.delete(mat2, 1, axis=1))
    C = +det(np.delete(mat2, 2, axis=1))
    D = -det(np.delete(mat2, 3, axis=1))
    E = +det(mat2[:, :-1])

    circle_center: npt.NDArray[np.float64] = -np.array([B, C, D]) / 2 / A
    radius: float = np.sqrt(B * B + C * C + D * D - 4 * A * E) / 2 / abs(A)
    angle = calculateArcAngle(circle_center, p1, p2, p3)

    return circle_center, radius, angle
