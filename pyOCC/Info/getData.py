import numpy as np
from OCC.Core.gp import *


def getPointsCenter(points_list: list[tuple[float, float, float]]):
    """
    计算点的中心坐标。

    Parameter
    ---------
    points (list of tuples): 包含点坐标的列表，每个点表示为一个元组 (x, y, z)。

    Return
    ------
    tuple: 中心点的坐标，格式为 (center_x, center_y, center_z)。
    """
    # 将点的坐标拆分成单独的列表
    x_coords, y_coords, z_coords = zip(*points_list)

    # 计算坐标的平均值，这将给出中心点
    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)
    center_z = np.mean(z_coords)

    # 返回中心点的坐标
    return (center_x, center_y, center_z)
