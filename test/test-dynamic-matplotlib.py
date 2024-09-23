import os
import random
import sys
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D

# pyOCC
from OCC.Core.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from dynamic.DHParameters import standard_DH2Transform
from dynamic.transform import TransformMatrix_4x4
from pyOCC import create_tetrahedron, createTrihedron, getColor, read_step, readStepWithColor

radian = np.deg2rad


def NDArray2gp_Trsf(ndarray: TransformMatrix_4x4):
    trsf = gp_Trsf()
    trsf.SetValues(*ndarray.flatten()[:-4])
    return trsf


def extract_axes(transformation_matrix):
    transformed_origin = np.matrix(
        [transformation_matrix[0, 3], transformation_matrix[1, 3], transformation_matrix[2, 3]]
    )
    # 提取单位矩阵的列作为基础轴向量
    # 提取前三列
    rotation_and_scale = transformation_matrix[:3, :3]
    # 输出三个行向量
    x_aixs = np.matrix([[1, 0, 0, 1]])
    y_aixs = np.matrix([[0, 1, 0, 1]])
    z_aixs = np.matrix([[0, 0, 1, 1]])
    transformed_x = x_aixs @ transformation_matrix
    transformed_y = y_aixs @ transformation_matrix
    transformed_z = z_aixs @ transformation_matrix
    print(transformed_z)
    return transformed_origin, transformed_x, transformed_y, transformed_z


# end def
LAST_POINT = np.matrix([[0], [0], [0], [1]])


def plot_coordinate_system(ax, transformation_matrix, label, axis_length=1.0):
    position = transformation_matrix[:3, 3]
    x_vector = transformation_matrix[:3, 0]
    y_vector = transformation_matrix[:3, 1]
    z_vector = transformation_matrix[:3, 2]

    # 计算各轴结束点的位置
    x_end = position + x_vector / np.linalg.norm(x_vector) * axis_length
    y_end = position + y_vector / np.linalg.norm(y_vector) * axis_length
    z_end = position + z_vector / np.linalg.norm(z_vector) * axis_length

    # 绘制坐标轴线
    ax.plot(
        [position[0, 0], x_end[0, 0]],
        [position[1, 0], x_end[1, 0]],
        [position[2, 0], x_end[2, 0]],
        color="g",
        linewidth=2,
    )
    ax.plot(
        [position[0, 0], y_end[0, 0]],
        [position[1, 0], y_end[1, 0]],
        [position[2, 0], y_end[2, 0]],
        color="b",
        linewidth=2,
    )
    ax.plot(
        [position[0, 0], z_end[0, 0]],
        [position[1, 0], z_end[1, 0]],
        [position[2, 0], z_end[2, 0]],
        color="r",
        linewidth=2,
    )

    # 连接两个点
    global LAST_POINT
    ax.plot(
        [LAST_POINT[0, 0], position[0, 0]],
        [LAST_POINT[1, 0], position[1, 0]],
        [LAST_POINT[2, 0], position[2, 0]],
        color="black",
    )
    LAST_POINT = position


# end def
def convert_to_list_of_dicts(dh_dict):
    dh_list = []
    keys = list(dh_dict.keys())

    for i in range(len(dh_dict[keys[0]])):
        dh_entry = {}
        for key in keys:
            dh_entry[key] = dh_dict[key][i]
        dh_list.append(dh_entry)

    return dh_list


if __name__ == "__main__":
    # 示例的齐次变换矩阵（假设这是你的变换矩阵）
    base = np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    # 创建一个空的 3D 画布
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    # 设置坐标轴的范围
    ax.set_xlim(-1000, 1000)
    ax.set_ylim(-1000, 1000)
    ax.set_zlim(0, 2000)
    # 调用函数画坐标轴
    plot_coordinate_system(ax, base, "Origin", axis_length=100.0)
    # DH = {
    #     "a": [0, 870, 225, 0, 0, 0],
    #     "d": [490, 0, 0, 1015, 0, 175],
    #     # "d": [0, 0, 0, -1015, 0, -(175 + 237.18)],
    #     "alpha": radian([90, 0, -90, -90, 90, 0]),
    #     "theta": radian([0, 0, 0, 0, 0, 0]),
    #     "offset": radian([0, 90, 0, 0, 0, 0]),
    # }
    DH = {
        "a": [320, 870, 225, 0, 0, 0],
        "d": [490, 300, 400, 1015, 0, 175],
        # "d": [0, 0, 0, -1015, 0, -(175 + 237.18)],
        "alpha": radian([-90, 0, 90, -90, 90, 0]),
        "theta": radian([0, 0, 0, 0, 0, 0]),
        "offset": radian([0, 90, 0, 0, 0, 0]),
    }

    # J1
    left_J1, right_J1 = standard_DH2Transform(
        a=DH["a"][0], d=DH["d"][0], alpha=DH["alpha"][0], theta=DH["theta"][0]
    )
    J1 = base @ left_J1
    # print(J1)
    plot_coordinate_system(ax, J1, "J1", axis_length=200.0)
    # J2
    left_J2, right_J2 = standard_DH2Transform(
        a=DH["a"][1], d=DH["d"][1], alpha=DH["alpha"][1], theta=DH["theta"][1]
    )
    J2 = J1 @ right_J1 @ left_J2
    # print(J2)
    plot_coordinate_system(ax, J2, "J2", axis_length=200.0)
    # J3
    left_J3, right_J3 = standard_DH2Transform(
        a=DH["a"][2], d=DH["d"][2], alpha=DH["alpha"][2], theta=DH["theta"][2]
    )

    # print(J3)
    plot_coordinate_system(ax, J3, "J3", axis_length=200.0)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Coordinate System")

    ax.legend()
    plt.show()
