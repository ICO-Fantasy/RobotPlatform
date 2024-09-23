import os
import sys
from typing import Callable

# pyOCC
from OCC.Core.Addons import Font_FA_Regular, Font_FontAspect_Italic, text_to_brep
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
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.gp import gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
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
from OCC.Core.NCollection import (
    NCollection_List,
    NCollection_String,
    NCollection_TListIterator,
    NCollection_Utf8String,
)
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.StdPrs import StdPrs_BRepFont, StdPrs_BRepTextBuilder
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopLoc import TopLoc_Location
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
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    box_shape = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    txt_Str = "AB"
    txt_Font = "SimSun"
    txt_Size = 10  # 字体大小 (两个字节的宽度)

    aFontAspect = Font_FA_Regular
    font_shape = text_to_brep(txt_Str, txt_Font, aFontAspect, txt_Size, True)  # 从文字生成 Face
    aPrismVec = gp_Vec(0, 0, 1)  # Vec face，进行 prism
    font_shape = BRepPrimAPI_MakePrism(font_shape, aPrismVec).Shape()  # 形成字符模板 TopoDS_Shape
    gui.display(AIS_Shape(font_shape), True)
    "========================================================================================"
    aFontAspect = Font_FontAspect_Italic
    font_shape = text_to_brep(
        txt_Str, txt_Font, Font_FontAspect_Italic, txt_Size, True
    )  # 从文字生成 Face
    aPrismVec = gp_Vec(0, 0, -1)  # Vec face，进行 prism
    font_shape = BRepPrimAPI_MakePrism(font_shape, aPrismVec).Shape()  # 形成字符模板 TopoDS_Shape
    the_trsf = gp_Trsf()
    the_trsf.SetTranslation(gp_Vec(0, 0, 10))
    font_shape.Location(TopLoc_Location(the_trsf))
    gui.display(AIS_Shape(font_shape), True)
    "========================================================================================"
    #! 只能是 Z 方向，下面在 X 方向创建无效
    aFontAspect = Font_FA_Regular
    font_shape = text_to_brep(
        txt_Str, txt_Font, Font_FontAspect_Italic, txt_Size, True
    )  # 从文字生成 Face
    aPrismVec = gp_Vec(1, 0, 0)  # Vec face，进行 prism
    font_shape = BRepPrimAPI_MakePrism(font_shape, aPrismVec).Shape()  # 形成字符模板 TopoDS_Shape
    the_trsf = gp_Trsf()
    the_trsf.SetTranslation(gp_Vec(0, 0, 0))
    font_shape.Location(TopLoc_Location(the_trsf))
    gui.display(AIS_Shape(font_shape), True)
    "========================================================================================"
    # font_name = "SimSun"
    # aFontAspect = Font_FA_Regular
    # font_Size = 10  # 字体大小 (两个字节的宽度)

    # 无法设置字体的搜索级别（Font_StrictLevel_Any）
    # brep_font = StdPrs_BRepFont(NCollection_String(font_name), aFontAspect, font_Size)
    # brep_text_builder = StdPrs_BRepTextBuilder()
    # brep_text = brep_text_builder.Perform(brep_font, NCollection_String("CD"), gp_Ax3())
    # gui.display(brep_text, True)
    "========================================================================================"

    ais_box = AIS_Shape(box_shape)
    ais_box.SetTransparency(0.3)
    gui.display(ais_box, True)
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
