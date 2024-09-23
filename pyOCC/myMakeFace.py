from itertools import permutations

from OCC.Core.AIS import AIS_Shape
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeVertex,
)
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.gp import *
from OCC.Core.TopoDS import TopoDS_Wire

colors = [
    (255, 0, 0),  # 红色 (Red)
    (255, 165, 0),  # 橙色 (Orange)
    (255, 255, 0),  # 黄色 (Yellow)
    (0, 128, 0),  # 绿色 (Green)
    (0, 255, 255),  # 青色 (Cyan)
    (0, 0, 255),  # 蓝色 (Blue)
    (128, 0, 128),  # 紫色 (Purple)
    (0, 0, 0),  # 黑色 (Black)
]


def makeFaceFromPoint(point1: gp_Pnt, point2: gp_Pnt, point3: gp_Pnt, point4: gp_Pnt, in_order=True):
    """
    默认按顺序输入四个点，创建一个面
    支持打乱顺序的四个点生成一个面(增大计算量)
    """
    # 使用这四个点来创建一个面
    # polygon_builder = BRepBuilderAPI_MakePolygon()
    # polygon_builder.Add(point1)
    # polygon_builder.Add(point2)
    # polygon_builder.Add(point3)
    # polygon_builder.Add(point4)
    # polygon_builder.Close()
    if in_order:
        polygon_builder = BRepBuilderAPI_MakePolygon(point1, point2, point3, point4, True)
        polygon_face = BRepBuilderAPI_MakeFace(polygon_builder.Wire(), True)
        shape = polygon_face.Face()
        if BRepCheck_Analyzer(shape).IsValid():
            return shape
        for p1, p2, p3, p4 in permutations([point1, point2, point3, point4], 4):
            polygon_builder = BRepBuilderAPI_MakePolygon(p1, p2, p3, p4, True)
            polygon_face = BRepBuilderAPI_MakeFace(polygon_builder.Wire(), True)
            shape = polygon_face.Face()
            if BRepCheck_Analyzer(shape).IsValid():
                return shape
        raise ValueError("四个点不在一个平面上")
    else:
        for p1, p2, p3, p4 in permutations([point1, point2, point3, point4], 4):
            polygon_builder = BRepBuilderAPI_MakePolygon(p1, p2, p3, p4, True)
            polygon_face = BRepBuilderAPI_MakeFace(polygon_builder.Wire(), True)
            shape = polygon_face.Face()
            if BRepCheck_Analyzer(shape).IsValid():
                return shape
        raise ValueError("四个点不在一个平面上")
    # end if


# end def

if __name__ == "__main__":
    from getColor import getColor
    from SimpleGui import initDisplay

    display, start_display, add_menu, add_function_to_menu = initDisplay()
    p1 = gp_Pnt(-33.8284, 25.5051, 53.3819)
    p2 = gp_Pnt(-33.8284, 25.5051, -145.0)
    p3 = gp_Pnt(-43.4607, 12.7294, 53.3819)
    p4 = gp_Pnt(-43.4607, 12.7294, -145.0)
    p5 = gp_Pnt(22.8355, -17.2169, 34.5254)
    p6 = gp_Pnt(22.8355, -17.2169, -145.0)
    p7 = gp_Pnt(13.2032, -29.9926, 38.0749)
    p8 = gp_Pnt(13.2032, -29.9926, -145.0)
    a1 = AIS_Shape(BRepBuilderAPI_MakeVertex(p1).Shape())
    a2 = AIS_Shape(BRepBuilderAPI_MakeVertex(p2).Shape())
    a3 = AIS_Shape(BRepBuilderAPI_MakeVertex(p3).Shape())
    a4 = AIS_Shape(BRepBuilderAPI_MakeVertex(p4).Shape())
    a5 = AIS_Shape(BRepBuilderAPI_MakeVertex(p5).Shape())
    a6 = AIS_Shape(BRepBuilderAPI_MakeVertex(p6).Shape())
    a7 = AIS_Shape(BRepBuilderAPI_MakeVertex(p7).Shape())
    a8 = AIS_Shape(BRepBuilderAPI_MakeVertex(p8).Shape())
    a1.SetColor(getColor(colors[0]))
    a2.SetColor(getColor(colors[1]))
    a3.SetColor(getColor(colors[2]))
    a4.SetColor(getColor(colors[3]))
    a5.SetColor(getColor(colors[4]))
    a6.SetColor(getColor(colors[5]))
    a7.SetColor(getColor(colors[6]))
    a8.SetColor(getColor(colors[7]))
    display.Context.Display(a1, True)
    display.Context.Display(a2, True)
    display.Context.Display(a3, True)
    display.Context.Display(a4, True)
    display.Context.Display(a5, True)
    display.Context.Display(a6, True)
    display.Context.Display(a7, True)
    display.Context.Display(a8, True)
    # f_1 = makeFaceFromPoint(p1, p3, p7, p5)
    # f_2 = makeFaceFromPoint(p2, p1, p5, p6)
    # f_3 = makeFaceFromPoint(p4, p2, p6, p8)
    # f_4 = makeFaceFromPoint(p3, p4, p8, p7)
    # af1 = AIS_Shape(f_1)
    # af2 = AIS_Shape(f_2)
    # af3 = AIS_Shape(f_3)
    # af4 = AIS_Shape(f_4)
    # display.Context.Display(af1, True)
    # display.Context.Display(af2, True)
    # display.Context.Display(af3, True)
    # display.Context.Display(af4, True)
    # w1 = BRepBuilderAPI_MakeEdge(p1, p2).Shape()
    # w2 = BRepBuilderAPI_MakeEdge(p3, p4).Shape()
    # w3 = BRepBuilderAPI_MakeEdge(p5, p6).Shape()
    # w4 = BRepBuilderAPI_MakeEdge(p7, p8).Shape()
    # aw1 = AIS_Shape(w1)
    # aw2 = AIS_Shape(w2)
    # aw3 = AIS_Shape(w3)
    # aw4 = AIS_Shape(w4)
    # aw1.SetColor(getColor(colors[0]))
    # aw2.SetColor(getColor(colors[1]))
    # aw3.SetColor(getColor(colors[2]))
    # aw4.SetColor(getColor(colors[3]))
    # display.Context.Display(aw1, True)
    # display.Context.Display(aw2, True)
    # display.Context.Display(aw3, True)
    # display.Context.Display(aw4, True)
    pp1 = p1
    pp2 = p3
    pp3 = p5
    pp4 = p7
    dir1 = gp_Dir(gp_Vec(pp1, pp2))
    dir2 = gp_Dir(gp_Vec(pp3, pp4))
    at1 = BRepBuilderAPI_MakeEdge(gp_Lin(pp1, dir1)).Shape()
    at2 = BRepBuilderAPI_MakeEdge(gp_Lin(pp3, dir2)).Shape()
    display.Context.Display(AIS_Shape(at1), True)
    display.Context.Display(AIS_Shape(at2), True)
    # f1 = makeFaceFromPoint(p1, p2, p4, p3)
    f1 = makeFaceFromPoint(p1, p3, p4, p2)
    display.Context.Display(AIS_Shape(f1), True)
    # print(BRepCheck_Analyzer(f1).IsValid())
    start_display()
# end main
