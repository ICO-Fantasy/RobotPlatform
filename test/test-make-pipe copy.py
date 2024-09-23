import math
import os
import sys
from itertools import cycle

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
        # region 增加一个按钮
        self._anime_list: list[AIS_Shape] = []
        self._iter_list = None
        button_layout = QVBoxLayout()
        a_h_layout = QHBoxLayout()
        button_layout.addLayout(a_h_layout)

        # next
        button = QPushButton("Next_Step")
        button.clicked.connect(self.next_step_func)
        button_layout.addWidget(button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas, 8)
        main_layout.addLayout(button_layout, 1)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # endregion

        self.setCentralWidget(central_widget)
        self.centerOnScreen()
        # 去掉窗口标题
        # self.setWindowFlags(Qt.FramelessWindowHint)

    # end alternate constructor
    @property
    def anime_list(self):
        return self._anime_list

    # end def
    @anime_list.setter
    def anime_list(self, value):
        self._anime_list = value
        self._iter_list = iter(value)

    # end def

    def next_step_func(self):
        ais_obj = next(self._iter_list)
        for ais in ais_obj:
            self.canvas.context.Display(ais, False)

        # self.v3d.FitAll()
        self.canvas.context.UpdateCurrentViewer()

    # end def

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
    # region test

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

    # xyz_list = [
    #     (325.5000, -5181.0000, -61.0000),
    #     (170.5000, -5181.0000, -61.0000),
    #     (170.5000, -5081.0000, -200.0000),
    #     (170.5000, -4808.0000, -200.0000),
    #     (170.5000, -4708.0000, 100.0000),
    #     (170.5000, -3208.0000, 100.0000),
    #     (170.5000, -3108.0000, 50.0000),
    #     (170.5000, -200.0000, 50.0000),
    #     (170.5000, 0.0000, 0.0000),
    #     (0.0000, 0.0000, 0.0000),
    # ]
    last_p = None
    # 彩虹颜色表
    color_list = [
        (255, 0, 0),
        (255, 165, 0),
        (0, 255, 0),
        (0, 255, 255),
        (0, 0, 255),
        (139, 0, 255),
    ]
    # color = cycle(color_list)
    # ais_list = []
    # for num, p in enumerate(xyz_list):
    #     # if num > 25:
    #     #     break
    #     point = gp_Pnt(*p)
    #     if last_p:
    #         the_color = next(color)
    #         a_vertex = BRepBuilderAPI_MakeVertex(point).Shape()
    #         ais_vertex = AIS_Shape(a_vertex)
    #         ais_vertex.SetColor(getColor(*the_color))

    #         a_edge = BRepBuilderAPI_MakeEdge(last_p, point).Shape()
    #         ais_shape = AIS_Shape(a_edge)
    #         ais_shape.SetColor(getColor(*the_color))
    #         # gui.canvas.viewer3d.Context.Display(ais_shape, False)
    #         ais_list.append((ais_vertex, ais_shape))

    #     last_p = point
    # # end for
    # gui.anime_list = ais_list

    xyz_list = [
        (325.5000, -5181.0000, -61.0000),
        (170.5000, -5181.0000, -61.0000),
        (170.5000, -5081.0000, -200.0000),
        (170.5000, -4808.0000, -200.0000),
        (170.5000, -4708.0000, 100.0000),
        (170.5000, -3208.0000, 100.0000),
        (170.5000, -3108.0000, 50.0000),
        (170.5000, -200.0000, 50.0000),
        (170.5000, 0.0000, 0.0000),
        (0.0000, 0.0000, 0.0000),
    ]

    last_p = None
    tempT = gp_Trsf()
    tempR = gp_Quaternion(gp_Vec(1, 0, 0), math.radians(194))
    tempT.SetRotationPart(tempR)
    for p in xyz_list:
        point = gp_Pnt(*p)
        if last_p:
            a_edge = BRepBuilderAPI_MakeEdge(last_p, point).Shape()
            a_edge = BRepBuilderAPI_Transform(a_edge, tempT).Shape()
            pipe_1 = AIS_Shape(a_edge)
            pipe_1.SetColor(getColor(255, 0, 0))
            pipe_1.SetWidth(2)
            gui.canvas.viewer3d.Context.Display(pipe_1, False)

        last_p = point
    # end for

    xyz_list = [
        (0.0, 0.0, 0.0),
        (170.5, 0.0, 0.0),
        (170.5, 206.2, 0.0),
        (170.5, 3027.3, 705.3),
        (170.5, 3136.5, 681.0),
        (170.5, 4591.7, 1044.8),
        (170.5, 4615.9, 1360.1),
        (170.5, 4880.8, 1426.4),
        (170.5, 5011.5, 1315.8),
        (325.5, 5011.5, 1315.8),
    ]

    last_p = None
    for p in xyz_list:
        point = gp_Pnt(*p)
        if last_p:
            a_edge = BRepBuilderAPI_MakeEdge(last_p, point).Shape()
            pipe_2 = AIS_Shape(a_edge)
            pipe_2.SetColor(getColor(0, 0, 255))
            pipe_2.SetWidth(5)
            pipe_2.SetTransparency()
            gui.canvas.viewer3d.Context.Display(pipe_2, False)

        last_p = point
    # end for
    gui.canvas.context.UpdateCurrentViewer()
    gui.canvas.viewer3d.FitAll()

    # endregion

    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    mainGUI()
# end main
