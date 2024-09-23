"""
用 np 数组表示的圆弧
符合右手坐标系，逆时针旋转为正
"""
from __future__ import annotations

import numpy as np
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GeomAbs import GeomAbs_CurveType
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Edge

from .Point import Point


class Arc:
    def __init__(self, radius=1.0, angle=2 * np.pi, center_point=None | Point, start_point=None | Point):
        """创建一个圆弧

        Parameters
        ----------
        `radius` : float, optional
            圆弧的半径，by default 1.0
        `angle` : float, optional
            圆弧的弧度角度，by default pi , 表示整圆，取值范围在 `[-2pi, 2pi]` 之间
        `center_point` : Point, optional
            圆心的坐标，by default None
        `start_point` : Point, optional
            圆弧的起始点坐标，by default None
        """
        self._radius = radius
        self._angle = angle
        self.center_point = center_point if center_point is not None else Point(0.0, 0.0, 0.0)
        self.start_point = start_point if start_point is not None else Point(0.0, 0.0, 0.0)

    # end default constructor
    def __add__(self, other: Arc):
        """定义加法操作"""
        if isinstance(other, Arc):
            pass

    # end def
    def __sub__(self, other: Arc):
        """定义减法操作"""
        if isinstance(other, Arc):
            pass

    # end def
    def __getitem__(self, index):
        """定义索引操作，使 Circle[0] 返回 self._radius, Circle[1] 返回 self._angle"""
        match index:
            case 0:
                return self._radius
            case 1:
                return self._angle
            case _:
                raise IndexError("Index out of range")
        # end match

    # end def
    def __str__(self):
        return f"(半径{self._radius}, 角度{self._angle}, 圆心{self.center_point}, 圆弧起点{self.start_point})"

    # end def
    def from_TopoDS_Edge(self, a_topo_arc: TopoDS_Edge) -> None:
        """读取 TopoDS_Edge 的数据到 Arc 对象

        Parameters
        ----------
        `a_topo_arc` : TopoDS_Edge
            OCC 的圆弧

        """
        brep = BRepAdaptor_Curve(a_topo_arc)
        if brep.GetType() == GeomAbs_CurveType.GeomAbs_Circle:
            brep.Circle().Radius()

    # end def
    def to_TopoDS_Edge(self) -> gp_Pnt:
        """将 Arc 对象输出为 TopoDS_Edge

        Returns
        -------
        gp_Pnt
        """
        return gp_Pnt(self._x, self._y, self._z)

    # end def
    def Normal(self):
        return Vector

    # end def


# end class
if __name__ == "__main__":
    # 创建 Point 对象
    point1 = Point(1.0, 2.0, 3.0)
    point2 = Point(4.0, 5.0, 6.0)

    # 参与 NumPy 计算
    result = point1 + point2
    print(result)  # 输出 [ 5.  7.  9.]
# end main
