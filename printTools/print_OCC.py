import math

import numpy as np
from colored import attr, bg, fg
from OCC.Core.gp import *


def _format_number(value, precision=4, tolerance=1e-10):
    if abs(value) < tolerance:
        return 0
    else:
        return value


def print_Trsf(T: gp_Trsf, precision=4, tolerance=1e-10, four_line=False, xyzwpr=False):
    """在 python 中打印 gp_Trsf"""
    if xyzwpr:
        print_Trsf_XYZWPR(T, precision)
        return None
    # pT = np.eye(4)
    # r = T.GetRotation()
    # Rm = r.GetMatrix()
    # for i in range(3):
    #     for j in range(3):
    #         pT[i][j] = Rm.Value(i + 1, j + 1)
    # x, y, z = T.Transforms()
    # pT[:3, 3] = [x, y, z]
    # with np.printoptions(precision):  # 指定打印的小数位数
    #     print(pT)
    out_str = str()
    for i in range(1, 4):
        for j in range(1, 5):
            value = _format_number(T.Value(i, j), tolerance=tolerance)
            if i in (1, 2, 3) and j in (1, 2, 3):
                out_str += (
                    f"{fg('red')}{(' ' if value >= 0 else '')}{value:.{precision}f}{attr(0)}, "
                )
            elif i in (1, 2, 3) and j == 4:
                out_str += (
                    f"{fg('blue')}{(' ' if value >= 0 else '')}{value:.{precision}f}{attr(0)}, "
                )
            else:
                out_str += f"{value:.{precision}f}, "
        out_str += "\n"
    if four_line:
        out_str += "0     , 0     , 0     , 1     "
        print(out_str)
    else:
        print(out_str[:-3])
    # return getTrsfValue(T)


def get_Trsf_value(the_trsf: gp_Trsf):
    return np.array(
        [
            [
                the_trsf.Value(1, 1),
                the_trsf.Value(1, 2),
                the_trsf.Value(1, 3),
                the_trsf.Value(1, 4),
            ],
            [
                the_trsf.Value(2, 1),
                the_trsf.Value(2, 2),
                the_trsf.Value(2, 3),
                the_trsf.Value(2, 4),
            ],
            [
                the_trsf.Value(3, 1),
                the_trsf.Value(3, 2),
                the_trsf.Value(3, 3),
                the_trsf.Value(3, 4),
            ],
            [0, 0, 0, 1],
        ]
    )


def get_gp_matrix(mat: gp_Mat):
    return np.array(
        [
            [
                mat.Value(1, 1),
                mat.Value(1, 2),
                mat.Value(1, 3),
            ],
            [
                mat.Value(2, 1),
                mat.Value(2, 2),
                mat.Value(2, 3),
            ],
            [
                mat.Value(3, 1),
                mat.Value(3, 2),
                mat.Value(3, 3),
            ],
        ]
    )


def print_Trsf_XYZWPR(trsf: gp_Trsf, precision=4):
    """以 gp_Extrinsic_XYZ 顺序打印欧拉角"""
    ar = trsf.GetRotation()
    x, y, z = trsf.Transforms()
    w, p, r = ar.GetEulerAngles(gp_EulerSequence.gp_Extrinsic_XYZ)
    str = ""
    str += f"x:{fg('red')}{x:.{precision}f}{attr(0)}, "
    str += f"y:{fg('green')}{y:.{precision}f}{attr(0)}, "
    str += f"z:{fg('blue')}{z:.{precision}f}{attr(0)}, "
    str += f"w:{fg('light_red')}{w:.{precision}f}{attr(0)}, "
    str += f"p:{fg('light_green')}{p:.{precision}f}{attr(0)}, "
    str += f"r:{fg('light_blue')}{r:.{precision}f}{attr(0)}"
    print(str)


def print_gp_Pnt(the_point: gp_Pnt, precision=4, get_str=False, colored=True):
    if colored:
        the_str = f"{fg('red')}{round(the_point.X(),precision)}{attr(0)}, {fg('green')}{round(the_point.Y(),precision)}{attr(0)}, {fg('blue')}{round(the_point.Z(),precision)}{attr(0)}"
    else:
        the_str = f"{round(the_point.X(),precision)}, {round(the_point.Y(),precision)}, {round(the_point.Z(),precision)}"

    if get_str:
        return the_str
    print(the_str)


def print_gp_Vec(the_vec: gp_Vec, precision=4):
    x, y, z = the_vec.X(), the_vec.Y(), the_vec.Z()
    print(
        f"{fg('red')}{x:.{precision}f}{attr(0)}, {fg('green')}{y:.{precision}f}{attr(0)}, {fg('blue')}{z:.{precision}f}{attr(0)}"
    )


if __name__ == "__main__":
    atrsf = gp_Trsf()
    print_Trsf(atrsf, four_line=True)
# end main
