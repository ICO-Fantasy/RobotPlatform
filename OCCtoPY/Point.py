from __future__ import annotations

import numpy as np
import numpy.typing as npt
from OCC.Core.gp import gp_Pnt

from .Vector import Vector


class Point:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """创建一个点

        Parameters
        ----------
        `x` : float, optional
            点的 X 坐标，by default 0.0
        `y` : float, optional
            点的 Y 坐标，by default 0.0
        `z` : float, optional
            点的 Z 坐标，by default 0.0
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # end default constructor
    def __add__(self, other: Point):
        """定义加法操作"""
        if isinstance(other, Point):
            # 检查是否是 Point 类型的对象
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise TypeError(f"Unsupported operand type for +: Point and {type(other)}")

    # end def
    def __sub__(self, other: Point):
        """定义减法操作"""
        if isinstance(other, Point):
            # 检查是否是 Point 类型的对象
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise TypeError(f"Unsupported operand type for -: Point and {type(other)}")

    # end def
    def __eq__(self, other):
        """定义如何比较两个 Point 对象是否相等"""
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return False

    # end def
    def __getitem__(self, index):
        """定义索引操作，使 Point[0] 返回 self._x, Point[1] 返回 self._y, Point[2] 返回 self._z"""
        match index:
            case 0:
                return self.x
            case 1:
                return self.y
            case 2:
                return self.z
            case _:
                raise IndexError("Index out of range")
        # end match

    # end def
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    # end def
    def from_gp_Pnt(self, a_gp_pnt: gp_Pnt) -> None:
        """读取 gp_Pnt 的数据到 Point 对象

        Parameters
        ----------
        a_gp_pnt : gp_Pnt
            OCC 的点
        """
        self.x = a_gp_pnt.X()
        self.y = a_gp_pnt.Y()
        self.z = a_gp_pnt.Z()

    # end def
    def to_gp_Pnt(self) -> gp_Pnt:
        """将 Point 对象输出为 gp_Pnt

        Returns
        -------
        gp_Pnt
        """
        return gp_Pnt(self.x, self.y, self.z)

    # end def
    def to_array(self) -> npt.NDArray[np.float_]:
        """返回点的 np 数组

        Returns
        -------
        NDArray[float_]
            _description_
        """
        return np.array([self.x, self.y, self.z])

    # end def
    def distanceBetween(self, other_point: Point) -> float:
        """计算与另一点之间的距离

        Parameters
        ----------
        `other_point` : Point

        Returns
        -------
        `distance` : float
        """
        # 定义两个点的坐标
        point1 = np.array([self.x, self.y, self.z])
        point2 = np.array([other_point.x, other_point.y, other_point.z])

        # 使用 NumPy 计算两点之间的距离
        return np.linalg.norm(point2 - point1)

    # end def
    def onVector(self, vector: Vector, LINEAR_TOLERANCE=1.0e-6, ANGLE_TOLERANCE=1.0e-8) -> bool:
        """判断点是否在线段上
        Parameters
        ----------
        vector : Vector
            线段
        LINEAR_TOLERANCE : _type_, optional
            线性公差，by default 1.0e-6
        ANGLE_TOLERANCE : _type_, optional
            角度公差，by default 1.0e-8

        Returns
        -------
        bool
            是否在线段上
        """
        """
        计算点到
        """
        startPoint, endPoint = vector.start_point, vector.endPoint()
        v1 = startPoint - self
        v2 = endPoint - self
        normV1 = np.linalg.norm(v1, 2)
        normV2 = np.linalg.norm(v2, 2)
        if normV1 < LINEAR_TOLERANCE or normV2 < LINEAR_TOLERANCE:
            return True
        else:
            cosTheta = np.dot(v1, v2) / (normV1 * normV2)
            if abs(cosTheta + 1.0) < ANGLE_TOLERANCE:
                return True
        return False


# end class
if __name__ == "__main__":
    # 创建 Point 对象
    point1 = Point(1.0, 2.0, 3.0)
    point2 = Point(4.0, 5.0, 6.0)

    # 参与 NumPy 计算
    result = point1 + point2
    print(result)  # 输出 [ 5.  7.  9.]
# end main
