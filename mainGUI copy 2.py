import os
import sys

from OCC.Core.AIS import AIS_Shape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool

# PySide6
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from pyOCC import getColor, readStep, readStepWithColor
from qtViewer3d import qtViewer3dWidget

# from test04 import ReadObjWithColor


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(self)
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

    # 2
    def makeline(p1, p2):
        a_line = BRepBuilderAPI_MakeEdge(l1, l2).Shape()
        gui.canvas.viewer3d.Context.Display(AIS_Shape(a_line), True)

    l1 = gp_Pnt(5324.59, 250.0, 700.0)
    l2 = gp_Pnt(4079.2, 250.0, 700.0)
    makeline(l1, l2)
    l1 = gp_Pnt(2469.99, 250.0, 700.0)
    l2 = gp_Pnt(2481.98, 250.0, 700.0)
    makeline(l1, l2)
    l1 = gp_Pnt(3799.62, 250.0, 700.0)
    l2 = gp_Pnt(2887.87, 250.0, 700.0)
    makeline(l1, l2)
    center = gp_Pnt(2470.0, 210.0, 700.0)
    shape_center = BRepBuilderAPI_MakeVertex(center).Shape()
    ais_center = AIS_Shape(shape_center)
    ais_center.SetColor(getColor(255, 255, 255))
    gui.canvas.viewer3d.Context.Display(ais_center, True)
    gui.canvas.viewer3d.FitAll()
    """test"""
    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    mainGUI()
# end main
