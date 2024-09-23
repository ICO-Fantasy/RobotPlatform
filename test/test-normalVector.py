import os
import sys
from typing import Callable

# pyOCC
from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_InteractiveObject,
    AIS_ListOfInteractive,
    AIS_NArray1OfEntityOwner,
    AIS_Shape,
    AIS_TexturedShape,
    AIS_ViewCube,
)
from OCC.Core.Aspect import Aspect_GradientFillMethod, Aspect_TypeOfTriedronPosition
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCC.Core.BRepGProp import BRepGProp_Face
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepTools import BRepTools_WireExplorer
from OCC.Core.GC import GC_MakeSegment
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
from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Shape, TopoDS_Wire, topods
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


def getNormal(face: TopoDS_Face):
    # 创建 BRepGProp_Face 对象
    prop = BRepGProp_Face(face)
    # 创建 BRepAdaptor_Surface 对象
    adaptor = BRepAdaptor_Surface(face)

    # 计算面的法线向量
    normalPnt = gp_Pnt()
    normal = gp_Vec()
    prop.Normal(adaptor.FirstUParameter(), adaptor.FirstVParameter(), normalPnt, normal)
    return normalPnt, normal


# end def
def makeFace(left_top: gp_Pnt, right_bottom: gp_Pnt, *radius: float) -> TopoDS_Face:
    # 左上角点
    p1 = left_top
    # 左下角点
    p2 = gp_Pnt(left_top.X(), right_bottom.Y(), left_top.Z())
    # 右下角点
    p3 = right_bottom
    # 右上角点
    p4 = gp_Pnt(right_bottom.X(), left_top.Y(), left_top.Z())

    # 创建边
    l1 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p1, p2).Value()).Edge()
    l2 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p2, p3).Value()).Edge()
    l3 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p3, p4).Value()).Edge()
    l4 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p4, p1).Value()).Edge()

    if not radius:
        # 创建线段
        wire = BRepBuilderAPI_MakeWire()
        wire.Add(l1)
        wire.Add(l2)
        wire.Add(l3)
        wire.Add(l4)

        # 创建面
        face = BRepBuilderAPI_MakeFace(wire.Wire())
        return face.Face()

    wire = BRepBuilderAPI_MakeWire()
    wire.Add(l1)
    wire.Add(l2)
    wire.Add(l3)
    wire.Add(l4)

    # 创建面
    face = BRepBuilderAPI_MakeFace(wire.Wire())

    filleter = BRepFilletAPI_MakeFillet2d(face.Face())
    explorer = BRepTools_WireExplorer(wire.Wire())
    while explorer.More():
        vertex = explorer.CurrentVertex()
        filleter.AddFillet(vertex, *radius)
        explorer.Next()
    filleter.Shape()

    a = filleter.Shape()
    b = topods.Face(a)
    return b


# end class
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    face = makeFace(gp_Pnt(-5, -5, 0), gp_Pnt(5, 5, 0))
    normalPnt, normal = getNormal(face)
    normal_shape = BRepBuilderAPI_MakeEdge(normalPnt, normalPnt.Translated(normal)).Shape()
    ais_normal = AIS_Shape(normal_shape)
    gui.display(AIS_Shape(face), True)
    gui.display(ais_normal, True)
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
