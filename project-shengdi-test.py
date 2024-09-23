import math
import os
import sys
from typing import Callable

# autocorrect:false
# 全局日志设置
from loguru import logger

if sys.stderr:
    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    # logger.add(sys.stderr, level="DEBUG")

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
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import (
    gp_Ax2,
    gp_Circ,
    gp_Dir,
    gp_EulerSequence,
    gp_Pnt,
    gp_Quaternion,
    gp_Trsf,
    gp_Vec,
)
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
from OCC.Extend.DataExchange import read_step_file, read_stl_file

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
    #"""
    # gui.canvas.set_display_mode("solid")
    gui.display(AIS_Shape_Tri(arrow_length=400))

    assembled_shape = read_step_file(r".\test-shengdi\模具自动喷砂方案.STEP")
    ais_assembled = AIS_Shape(assembled_shape)
    # a_trsf = gp_Trsf()
    # a_trsf.SetTranslation(gp_Vec(3, 2, 6))
    # ais_robot.SetLocalTransformation(a_trsf)
    ais_assembled.SetColor(getColor(125, 125, 125))
    ais_assembled.SetTransparency(0.4)
    gui.display(ais_assembled, False)

    robot_shape = read_step_file(r".\test-shengdi\DEFAULT-710iC-test01.STEP")
    # robot_shape = read_step_file(r".\test-shengdi\DEFAULT-710iC-test01.STEP")
    ais_robot = AIS_Shape(robot_shape)
    a_trsf = gp_Trsf()
    a_trsf.SetTranslation(gp_Vec(-695.20, -1.44, -198.66))
    ais_robot.SetLocalTransformation(a_trsf)
    ais_robot.SetColor(getColor(247, 217, 61))
    gui.display(ais_robot, False)

    crew_shape = read_step_file(r".\test-shengdi\喷砂房改造-喷头装配体.STEP")
    # craw_shape = read_step_file(r".\test-shengdi\DEFAULT-710iC-test01.STEP")
    ais_crew = AIS_Shape(crew_shape)
    a_trsf = gp_Trsf()
    a_trsf.SetTranslationPart(gp_Vec(645.80, -36.94, 1406.34))
    a_quat = gp_Quaternion()
    a_quat.SetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX, 0, math.radians(90), -math.radians(90))
    a_trsf.SetRotationPart(a_quat)
    ais_crew.SetLocalTransformation(a_trsf)
    ais_crew.SetColor(getColor(214, 207, 199))
    gui.display(ais_crew, False)

    tool_shape = AIS_Shape_Tri(BRepBuilderAPI_MakeVertex(gp_Pnt(950.80, -56.94, 1361.11)).Shape())
    gui.display(tool_shape, False)

    # model_shape = read_stl_file(r".\test-shengdi\2-68e-xm.STL")
    model_shape = read_step_file(r".\test-shengdi\2-68e-xm.STEP")
    ais_model = AIS_Shape(model_shape)
    a_trsf = gp_Trsf()
    a_trsf.SetTranslation(gp_Vec(1075.12, 45.44, -828.02))
    ais_model.SetLocalTransformation(a_trsf)
    ais_model.SetColor(getColor(216, 224, 255))
    gui.display(ais_model, False)

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
