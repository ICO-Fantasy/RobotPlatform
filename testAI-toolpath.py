import os
import sys
from pprint import pprint
from typing import Callable

# pyOCC
from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_InteractiveObject,
    AIS_Line,
    AIS_ListOfInteractive,
    AIS_NArray1OfEntityOwner,
    AIS_Point,
    AIS_Shape,
    AIS_TexturedShape,
    AIS_ViewCube,
)
from OCC.Core.Aspect import Aspect_GradientFillMethod, Aspect_TypeOfTriedronPosition
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.Geom import Geom_CartesianPoint, Geom_Line
from OCC.Core.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.Graphic3d import (
    Graphic3d_Camera,
    Graphic3d_GraduatedTrihedron,
    Graphic3d_NOM_ALUMINIUM,
    Graphic3d_NOM_STEEL,
    Graphic3d_RenderingParams,
    Graphic3d_RM_RASTERIZATION,
    Graphic3d_StereoMode_QuadBuffer,
    Graphic3d_StructureManager,
    Graphic3d_TransformPers,
    Graphic3d_TransModeFlags,
    Graphic3d_Vec2i,
)
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.NCollection import NCollection_List, NCollection_TListIterator
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Shape, TopoDS_Wire, topods
from OCC.Core.V3d import V3d_View
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Display.OCCViewer import Viewer3d

# PySide6
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from pyOCC import createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget

Dislpay = Callable[[AIS_InteractiveObject, bool], None]


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(
            self,
            bg_color_aspect=(
                (37, 55, 113),
                (36, 151, 132),
                Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
            ),
            selection_color=(13, 141, 255),
        )
        self.display = self.canvas.viewer3d.Context.Display
        self.context = self.canvas.viewer3d.Context
        self.view = self.canvas.viewer3d.View
        self.v3d = self.canvas.viewer3d
        self.setCentralWidget(self.canvas)
        self.centerOnScreen()

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


# end class
def read_tool_path(file_path: str):
    # 读取文件每一行为一个列表
    with open(file_path, "r") as f:
        lines = f.readlines()
        # 创建一个空的列表，用于存储读取到的数据
        data = []
        # 遍历每一行数据
        for line in lines:
            # 每行数据都包含 XYZ、IJK 的坐标
            line_tmp = line.strip().split("   ")
            a_line = {
                "x": float(line_tmp[0]),
                "y": float(line_tmp[1]),
                "z": float(line_tmp[2]),
                "i": float(line_tmp[3]),
                "j": float(line_tmp[4]),
                "k": float(line_tmp[5]),
            }
            data.append(a_line)
        # 返回 data 列表
        return data


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    tool_path = read_tool_path(r".\testAI-toolpath-data.txt")
    # pprint(tool_path)
    for p in tool_path:
        aisPoint = AIS_Point(Geom_CartesianPoint(p["x"], p["y"], p["z"]))
        line = BRepBuilderAPI_MakeEdge(
            gp_Pnt(p["x"], p["y"], p["z"]),
            gp_Pnt(p["x"], p["y"], p["z"]).Translated(
                gp_Vec(p["i"], p["j"], p["k"]).Normalized().Multiplied(0.5),
            ),
        )
        aisLine = AIS_Shape(line.Edge())
        gui.display(aisPoint, False)
        gui.display(aisLine, False)
    gui.view.Update()
    gui.v3d.FitAll()


# end def
def mainGUI():
    app = QApplication().instance()
    if not app:
        app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    gui.canvas.InitDriver()
    gui.canvas.qApp = app
    test(gui)
    # 窗口置顶
    gui.raise_()
    app.exec()


# end def
if __name__ == "__main__":
    mainGUI()
# end main
