import math

import numpy as np
from colored import attr, bg, fg
from OCC.Core.gp import *


def format_number(value, precision=4, tolerance=1e-10):
    if abs(value) < tolerance:
        return 0
    else:
        return value


def printTrsf(T: gp_Trsf, precision=4, tolerance=1e-10, four_line=False, xyzwpr=False):
    """在python中打印gp_Trsf"""
    if xyzwpr:
        printXYZWPR(T, precision)
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
    outstr = str()
    for i in range(1, 4):
        for j in range(1, 5):
            value = format_number(T.Value(i, j), tolerance=tolerance)
            if i in (1, 2, 3) and j in (1, 2, 3):
                outstr += f"{fg('red')}{(' ' if value >= 0 else '')}{value:.{precision}f}{attr(0)}, "
            elif i in (1, 2, 3) and j == 4:
                outstr += f"{fg('blue')}{(' ' if value >= 0 else '')}{value:.{precision}f}{attr(0)}, "
            else:
                outstr += f"{value:.{precision}f}, "
        outstr += "\n"
    if four_line:
        outstr += "0     , 0     , 0     , 1     "
        print(outstr)
    else:
        print(outstr[:-3])
    # return getTrsfValue(T)


def getTrsfValue(atrsf: gp_Trsf):
    return np.array(
        [
            [atrsf.Value(1, 1), atrsf.Value(1, 2), atrsf.Value(1, 3), atrsf.Value(1, 4)],
            [atrsf.Value(2, 1), atrsf.Value(2, 2), atrsf.Value(2, 3), atrsf.Value(2, 4)],
            [atrsf.Value(3, 1), atrsf.Value(3, 2), atrsf.Value(3, 3), atrsf.Value(3, 4)],
            [0, 0, 0, 1],
        ]
    )


def getgpMat(mat: gp_Mat):
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


def printXYZWPR(trsf: gp_Trsf, precision=4):
    """以gp_Extrinsic_XYZ顺序打印欧拉角"""
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


def printPnt(apnt: gp_Pnt, precision=4):
    print(f"{round(apnt.X(),precision)}, {round(apnt.Y(),precision)}, {round(apnt.Z(),precision)}")


def printVec(avec: gp_Vec, precision=4):
    x, y, z = avec.X(), avec.Y(), avec.Z()
    print(
        f"{fg('red')}{x:.{precision}f}{attr(0)}, {fg('green')}{y:.{precision}f}{attr(0)}, {fg('blue')}{z:.{precision}f}{attr(0)}"
    )


if __name__ == "__main__":
    atrsf = gp_Trsf()
    printTrsf(atrsf, four_line=True)
# end main
