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

from pyOCC import getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget


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
    from OCC.Extend.DataExchange import read_stl_file

    stl_shape = read_stl_file("2_InputRough_new.stl")
    ais_test = AIS_Shape(stl_shape)
    # # 创建 XCAF 应用程序和文档
    # an_app = XCAFApp_Application.GetApplication().GetApplication()
    # a_doc = an_app.NewDocument("MDTV-XCAF")
    # # 创建 RWObj_CafReader
    # obj_reader = RWObj_CafReader()
    # obj_reader.SetSinglePrecision(True)
    # system_unit = obj_reader.SystemLengthUnit()
    # obj_reader.SetSystemLengthUnit(system_unit * 0.001)
    # obj_reader.SetSystemCoordinateSystem(RWMesh_CoordinateSystem_Zup)
    # obj_reader.SetFileLengthUnit(0.001)
    # obj_reader.SetFileCoordinateSystem(RWMesh_CoordinateSystem_Zup)
    # obj_reader.SetDocument(a_doc)
    # # 读取 OBJ 文件
    # filename = "path/to/your/file.obj"
    # message = Message_ProgressRange()
    # obj_reader.Perform(filename, message)
    # # 获取形状
    # root_label = a_doc.Main()
    # shapes = XCAFDoc_DocumentTool.ShapeTool(root_label)
    # ref_shape = shapes.GetShape(root_label)
    # ais_test = ReadObjWithColor("blade_mesh.obj")
    # ais_test = ReadObjWithColor("maichongchuanganqi.obj")
    # 显示 AIS_Shape
    # ais_shape = AIS_Shape(ref_shape)
    # ais_test.SetColor(getColor(255, 0, 0))  # 设置颜色为红色
    gui.canvas.viewer3d.Context.Display(ais_test, False)
    gui.canvas.viewer3d.Context.Redisplay(ais_test, True)
    # gui.canvas.viewer3d.FitAll()
    "修改 AIS 对应的 TopoDShape"
    # a_box = BRepPrimAPI_MakeBox(5, 5, 5).Shape()
    # ais_box = AIS_Shape(a_box)
    # # print("ais_box:", id(ais_box))
    # gui.canvas.viewer3d.Context.Display(ais_box, True)
    # gui.canvas.viewer3d.FitAll()
    # new_box = BRepPrimAPI_MakeBox(5, 2, 5).Shape()
    # ais_box.SetShape(new_box)
    # # gui.canvas.viewer3d.Context.Display(ais_box, True)
    # gui.canvas.viewer3d.Context.Redisplay(ais_box, True)

    # # Set shape transparency, a float number from 0.0 to 1.0
    # context.SetTransparency(aisShape, 0, True)

    # shape=
    # ais = AIS_Shape(shape)
    # ais.SetColor(color)
    # gui.canvas.viewer3d.Context.Display(ais, True)
    # gui.canvas.viewer3d.DisplayMessage("中文测试", gp_Pnt(500, 5, 5), font_height=50)
    # gui.canvas.viewer3d.DisplayMessageOnScreen("屏幕显示测试")

    # gui.canvas.viewer3d.register_select_callback(move_ais)  # 注册选择回调函数
    gui.canvas.viewer3d.FitAll()
    """test"""
    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    mainGUI()
# end main
