from typing import TypeVar

from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepGProp import BRepGProp_Face
from OCC.Core.gp import gp_Vec
from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Shape

Topo = TypeVar("Topo", TopoDS_Shape, TopoDS_Edge)


def getTwoPoint(topo_edge: Topo):
    "找到 Edge 上两端点 (圆弧也适用)"
    brep_edge = BRepAdaptor_Curve(topo_edge)
    start_param = brep_edge.FirstParameter()
    end_param = brep_edge.LastParameter()
    start_point = brep_edge.Value(start_param)
    end_point = brep_edge.Value(end_param)
    return start_point, end_point


# end def

# def getEdgePoint(edge: TopoDS_Edge | TopoDS_Shape):
#     be_1 = BRepAdaptor_Curve(edge)  # type: ignore
#     p1 = be_1.Value(be_1.FirstParameter())
#     p2 = be_1.Value(be_1.LastParameter())
#     return p1, p2
# # end def
if __name__ == "__main__":
    import math

    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_MakeEdge,
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_MakeWire,
    )
    from OCC.Core.Geom import Geom_Circle, Geom_TrimmedCurve
    from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Wire
    from OCC.Display.SimpleGui import init_display

    # 创建一个点作为圆的圆心
    center = gp_Pnt(0.0, 0.0, 0.0)
    direction = gp_Dir(1, 0, 0)
    # 指定圆的半径
    radius = 5.0
    # 创建一个圆的几何对象
    circle = Geom_Circle(gp_Ax2(center, direction), radius)
    # 创建一个边
    edge = BRepBuilderAPI_MakeEdge(circle, 0, math.pi / 4).Edge()
    a0, a1 = getTwoPoint(edge)
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(edge)
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
    from printTools import print_gp_Pnt

    print_gp_Pnt(a0)
    print_gp_Pnt(a1)
    start_display()
# end main
