import os
import sys

from context import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(self)
        self.set_background_color(
            (37, 55, 113),
            (36, 151, 132),
            Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
        )
        self.setCentralWidget(self.canvas)
        self.centerOnScreen()
        # 去掉窗口标题
        # self.setWindowFlags(Qt.FramelessWindowHint)

    # end alternate constructor
    def centerOnScreen(self):
        # 获取屏幕的尺寸
        primary_screen = QGuiApplication.primaryScreen().size()
        size = self.geometry()
        x = (primary_screen.width() - size.width()) // 2
        y = 0.7 * (primary_screen.height() - size.height()) // 2
        # 移动主窗口到中心位置
        self.move(x, y)

    # end def
    def set_background_color(self, color1=None, color2=None, fill_method=None):
        """ """
        if color1 and color2 and fill_method:
            pass
        else:
            color1, color2, fill_method = self._bg_gradient_color
        self.canvas.viewer3d.View.SetBgGradientColors(
            getColor(color1), getColor(color2), fill_method, True
        )


def read_point(file_path, gui):
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

    point_list = []
    with open(file_path, "r") as f:
        for i in f:
            x, y, z = i.split(" ")
            # print(f"x:{x},y:{y},z:{z}")
            a_pnt = gp_Pnt(float(x), float(y), float(z))
            point_list.append(a_pnt)
    # end open file
    point_list
    for pnt in point_list:
        a_point_shape = BRepBuilderAPI_MakeVertex(pnt).Shape()
        a_ais_point = AIS_Shape(a_point_shape)
        gui.canvas.viewer3d.Context.Display(a_ais_point, False)
    gui.canvas.viewer3d.Context.UpdateCurrent()


# end def
def mainGUI():
    app = QApplication().instance()
    if not app:
        app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    gui.canvas.InitDriver()
    gui.canvas.qApp = app

    # 设置鼠标滑过时显示选择对象
    gui.canvas.viewer3d.Context.SetAutoActivateSelection(True)
    # 设置选择时的颜色
    aHighlightStyle = gui.canvas.viewer3d.Context.HighlightStyle()
    aHighlightStyle.SetColor(getColor(0, 125, 125))
    # 开启抗锯齿
    gui.canvas.viewer3d.EnableAntiAliasing()
    # gui.canvas.viewer3d.Context.HilightWithColor()
    """test"""
    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_MakeEdge,
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_MakeVertex,
        BRepBuilderAPI_MakeWire,
    )
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
    from OCC.Core.gp import gp_Ax2, gp_Circ, gp_Dir
    from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Shape, TopoDS_Wire

    from pyOCC import createTrihedron

    # origin_pnt=gp_Pnt(5340.0, 250.0, 700.0)
    origin_trsf = gp_Trsf()
    origin_trsf.SetTranslationPart(gp_Vec(5340.0, 250.0, 700.0))
    origin_trihedron = createTrihedron(origin_trsf)
    gui.canvas.viewer3d.Context.Display(origin_trihedron, True)
    # 2
    l1 = gp_Pnt(5373.29, 262.875, 700.0)
    l2 = gp_Pnt(5300.0, 342.0, 700.0)
    center = gp_Pnt(5340.0, 210.0, 700.0)
    # l1 = gp_Pnt(2430.0, 210.003, 700.0)
    # l2 = gp_Pnt(2430.0, 222.002, 700.0)
    # center = gp_Pnt(2469.99, 210.004, 700.0)
    p1 = gp_Pnt(5327.6406, 248.0425, 700.0)
    p2 = gp_Pnt(5340.0, 250.0001, 700.0)
    shape_p1 = BRepBuilderAPI_MakeVertex(p1).Shape()
    shape_p2 = BRepBuilderAPI_MakeVertex(p2).Shape()
    ais_p1 = AIS_Shape(shape_p1)
    ais_p2 = AIS_Shape(shape_p2)
    ais_p1.SetColor(getColor(0, 255, 0))
    ais_p2.SetColor(getColor(0, 255, 0))
    gui.canvas.viewer3d.Context.Display(ais_p1, True)
    gui.canvas.viewer3d.Context.Display(ais_p2, True)
    # p3 = gp_Pnt(2457.6306, 248.0425, 700.0)
    # p4 = gp_Pnt(2469.99, 250.0001, 700.0)
    # shape_p3 = BRepBuilderAPI_MakeVertex(p3).Shape()
    # shape_p4 = BRepBuilderAPI_MakeVertex(p4).Shape()
    # ais_p3 = AIS_Shape(shape_p3)
    # ais_p4 = AIS_Shape(shape_p4)
    # ais_p3.SetColor(getColor(255, 0, 0))
    # ais_p4.SetColor(getColor(255, 0, 0))
    # gui.canvas.viewer3d.Context.Display(ais_p3, True)
    # gui.canvas.viewer3d.Context.Display(ais_p4, True)
    # # 0.5
    # p5 = gp_Pnt(2430.0, 210.0, 700.0)
    # p6 = gp_Pnt(2437.6393, 186.4886, 700.0)
    # shape_p5 = BRepBuilderAPI_MakeVertex(p5).Shape()
    # shape_p6 = BRepBuilderAPI_MakeVertex(p6).Shape()
    # ais_p5 = AIS_Shape(shape_p5)
    # ais_p6 = AIS_Shape(shape_p6)
    # ais_p5.SetColor(getColor(0, 0, 255))
    # ais_p6.SetColor(getColor(0, 0, 255))
    # gui.canvas.viewer3d.Context.Display(ais_p5, True)
    # gui.canvas.viewer3d.Context.Display(ais_p6, True)
    # p7 = gp_Pnt(2508.0285, 222.3634, 700.0)
    # p8 = gp_Pnt(2509.9861, 210.004, 700.0)
    # shape_p7 = BRepBuilderAPI_MakeVertex(p7).Shape()
    # shape_p8 = BRepBuilderAPI_MakeVertex(p8).Shape()
    # ais_p7 = AIS_Shape(shape_p7)
    # ais_p8 = AIS_Shape(shape_p8)
    # ais_p7.SetColor(getColor(0, 0, 0))
    # ais_p8.SetColor(getColor(0, 0, 0))
    # gui.canvas.viewer3d.Context.Display(ais_p7, True)
    # gui.canvas.viewer3d.Context.Display(ais_p8, True)
    # dir = gp_Dir(
    #     0.0,
    #     0.0,
    #     1.0,
    # )
    a_line = BRepBuilderAPI_MakeEdge(l1, l2).Shape()

    print(center.Distance(p1))
    print(center.Distance(p2))
    shape_center = BRepBuilderAPI_MakeVertex(center).Shape()
    # shape_dir=
    ais_center = AIS_Shape(shape_center)
    # ais_dir=AIS_Shape(shape_dir)
    ais_center.SetColor(getColor(255, 255, 255))
    # ais_dir.SetColor(getColor(255,0,0))
    # ais_shape.SetColor(getColor(255, 0, 0))  # 设置颜色为红色
    gui.canvas.viewer3d.Context.Display(AIS_Shape(a_line), True)
    gui.canvas.viewer3d.Context.Display(ais_center, True)
    # 显示 AIS_Shape
    # a_circle = gp_Circ(gp_Ax2(center, dir), 40)
    # # last_segment = BRepBuilderAPI_MakeEdge(a_circle).Shape()
    # p1_vec = gp_Vec(center, p1)
    # p1_vec.Normalize()
    # p1_vec.Multiply(40)
    # p2_vec = gp_Vec(center, p2)
    # p2_vec.Normalize()
    # p2_vec.Multiply(40)
    # p1 = center.Translated(p1_vec)
    # p2 = center.Translated(p2_vec)
    # egmk = BRepBuilderAPI_MakeEdge(a_circle, p2, p1)
    # last_segment = egmk.Shape()
    # test_circe = gp_Circ(gp_Ax2(gp_Pnt(), gp_Dir(0, 0, 1)), 5)
    # last_segment = BRepBuilderAPI_MakeEdge(test_circe, 3.1415 * 1.5, 3.1415 * 2).Shape()
    # gui.canvas.viewer3d.Context.Display(AIS_Shape(last_segment), True)
    gui.canvas.viewer3d.FitAll()
    """test"""
    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    mainGUI()
# end main
