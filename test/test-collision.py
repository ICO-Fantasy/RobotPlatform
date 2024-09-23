import os
import sys

from loguru import logger

if sys.stderr:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_NArray1OfEntityOwner,
    AIS_Shape,
    AIS_Triangulation,
    AIS_ViewCube,
)
from OCC.Core.Aspect import Aspect_GradientFillMethod, Aspect_TypeOfTriedronPosition
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
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
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_ShapeEnum
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import (
    TopoDS_Builder,
    TopoDS_Compound,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shape,
    TopoDS_Wire,
    topods,
)
from OCC.Core.V3d import V3d_View
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Display.OCCViewer import Viewer3d

# PySide6
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from pyOCC import createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        # 去掉窗口标题
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.canvas = qtViewer3dWidget(self)
        self.display = self.canvas.viewer3d.Context.Display
        self.context = self.canvas.viewer3d.Context
        self.view = self.canvas.viewer3d.View
        self.v3d = self.canvas.viewer3d
        self.setCentralWidget(self.canvas)
        # self.view.SetBgGradientColors(getColor(40, 40, 40), getColor(170, 170, 170), Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical, True)
        self.view.SetBgGradientColors(
            getColor(37, 55, 113),
            getColor(36, 151, 132),
            Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
            True,
        )
        # 开启抗锯齿
        self.canvas.viewer3d.EnableAntiAliasing()
        self.centerOnScreen()

        # # 设置视图为隐藏线模式 (HLR)
        # gui.v3d.SetModeHLR()

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
    # 创建 box A
    box_A_shape = BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape()
    # 创建 box B
    box_B_shape = BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape()
    # box A 变换
    box_A_trsf = gp_Trsf()
    # box B 变换
    box_B_trsf = gp_Trsf()
    box_B_trsf.SetTranslation(gp_Vec(4.0, 4.0, 2.0))
    # 创建显示对象
    box_A_ais = AIS_Shape(box_A_shape)
    box_B_ais = AIS_Shape(box_B_shape)
    # 对 ais 对象执行变换
    box_A_ais.SetLocalTransformation(box_A_trsf)
    box_B_ais.SetLocalTransformation(box_B_trsf)
    # 干涉检测
    collision_faces = ais_collision_calculator(box_A_ais, box_B_ais)
    # 显示
    gui.display(box_A_ais, True)
    gui.display(box_B_ais, True)
    # 显示干涉的几个面
    if collision_faces:
        for f in collision_faces:
            f_ais = AIS_Shape(f)
            f_ais.SetColor(getColor(255, 0, 0))
            gui.display(f_ais, True)
    gui.v3d.FitAll()


# end def
def ais_pipe_collision(pipe: AIS_Shape, machines: list[AIS_Shape]):
    """对 AIS 管件和机器进行干涉判断的封装

    Parameters
    ----------
    `pipe` : AIS_Shape
        需要做干涉判断的管件
    `machines` : list[AIS_Shape]
        需要做干涉判断的机器

    Returns
    -------
    list[AIS_Shape]
        干涉判断的结果，如果无干涉返回空列表，否则返回发生碰撞的机器 AIS 列表
    """
    collision_result = []
    for machine in machines:
        # collision_result.extend(ais_collision_calculator(pipe, machine, False, True))
        if ais_collision_calculator(pipe, machine, False, True):
            collision_result.append(machine)
    return collision_result


# end def
"""
BRepMesh_IncrementalMesh

Parameters
----------
theShape: TopoDS_Shape
    参数类型：const TopoDS_Shape&
    描述：要进行网格化的形状。
theLinDeflection: float
    参数类型：const Standard_Real
    描述：线性偏差，控制三角化中的线性细节。
    它定义了离散化过程中生成的三角形的最大边长。
    较小的值会产生更精细的网格，但也会增加计算时间和内存需求。
    通常以模型单位为参考，表示在模型中的线性尺寸。
isRelative: bool (optional, default to Standard_False)
    参数类型：const Standard_Boolean（默认值：Standard_False）
    描述：是否使用相对值。
    如果设置为 Standard_True，则 theLinDeflection 用于每条边的离散化，其值为 <theLinDeflection> * <size of edge>。
    而对于面的离散化，使用它们边缘的最大偏差。
theAngDeflection: float (optional, default to 0.5)
    参数类型：const Standard_Real（默认值：0.5）
    描述：角度偏差，用于控制三角化中的角度细节。
    它定义了生成的三角形中最大角度的上限。较小的值会产生更细致的网格。
isInParallel: bool (optional, default to Standard_False)
    参数类型：const Standard_Boolean（默认值：Standard_False）
    描述：是否使用并行计算进行网格生成。
    如果设置为 Standard_True，则形状将在并行模式下进行网格生成。这在处理大型模型时可能提高性能。

Return
-------
None

"""


def ais_collision_calculator(
    ais_a: AIS_Shape, ais_b: AIS_Shape, get_collision_a=True, get_collision_b=True
):
    # 获取 AIS 对象的 TopoDS
    shape_a = ais_a.Shape()
    shape_b = ais_b.Shape()
    # 获取 AIS 对象的 Trsf
    trsf_a = ais_a.Transformation()
    trsf_b = ais_b.Transformation()
    # 移动原有的 shape
    shape_a = BRepBuilderAPI_Transform(shape_a, trsf_a).Shape()
    shape_b = BRepBuilderAPI_Transform(shape_b, trsf_b).Shape()
    # 生成网格
    mesh_a = BRepMesh_IncrementalMesh(shape_a, 1, False, 0.5, False)
    # mesh_a.Perform() #会自动调用 Perform()
    mesh_b = BRepMesh_IncrementalMesh(shape_b, 1, False, 0.5, False)
    # mesh_b.Perform() #会自动调用 Perform()
    # 碰撞检查
    checker = BRepExtrema_ShapeProximity(shape_a, shape_b, 0.1)
    checker.Perform()  # 需要手动调用 Perform()
    if checker.IsDone():
        # 获取 shape_a 的碰撞部分
        if get_collision_a:
            overlaps1 = checker.OverlapSubShapes1()
            face_indices1 = overlaps1.Keys()
            collision_face_a = []
            for ind in face_indices1:
                face = checker.GetSubShape1(ind)
                collision_face_a.append(face)

        # 获取 shape_b 的碰撞部分
        if get_collision_b:
            overlaps2 = checker.OverlapSubShapes2()
            face_indices2 = overlaps2.Keys()
            collision_face_b = []
            for ind in face_indices2:
                face = checker.GetSubShape2(ind)
                collision_face_b.append(face)
        # 返回发生干涉的面
        if collision_face_a or collision_face_b:
            return [*collision_face_a, *collision_face_b]
    else:
        logger.warning(f"干涉判断失败")
        return []


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
    # *两种变换方法等价
    # box_B_shape.Location(TopLoc_Location(box_B_trsf))
    # box_B_shape = BRepBuilderAPI_Transform(box_B_shape, box_B_trsf).Shape()
# end main
