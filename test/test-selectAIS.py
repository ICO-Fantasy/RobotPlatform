import os
import sys

from OCC.Core.AIS import AIS_InteractiveContext, AIS_NArray1OfEntityOwner, AIS_Shape, AIS_ViewCube
from OCC.Core.Aspect import (
    Aspect_GradientFillMethod,
    Aspect_TypeOfMarker,
    Aspect_TypeOfTriedronPosition,
)
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
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

from pyOCC import createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget

# from test04 import ReadObjWithColor


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(self)
        # self.set_background_color((40, 40, 40), (170, 170, 170), Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical)
        # self.set_background_color((37, 55, 113), (36, 151, 132), Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical)
        self.setCentralWidget(self.canvas)
        self.centerOnScreen()

        # 开启抗锯齿
        self.canvas.viewer3d.EnableAntiAliasing()

    # end alternate constructor
    @property
    def display(self):
        return self.canvas.viewer3d.Context.Display

    # end property
    @property
    def context(self):
        return self.canvas.viewer3d.Context

    # end property
    @property
    def view(self):
        return self.canvas.viewer3d.View

    # end property
    @property
    def v3d(self):
        return self.canvas.viewer3d

    # end property
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
        self.view.SetBgGradientColors(getColor(color1), getColor(color2), fill_method, True)

    # end def


# end class
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
def test(gui: MainWindow):
    test_list: list[AIS_Shape] = []
    # 设置鼠标滑过时显示选择对象
    # gui.context.SetAutoActivateSelection(False)
    # 设置高亮时的颜色
    aHighlightStyle = gui.context.HighlightStyle()
    aHighlightStyle.SetColor(getColor(255, 0, 0))
    # 创建 box
    box_shape = BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape()
    # ais_box = AIS_Shape(box_shape)
    # ais_box.SetColor(Quantity_Color(Graphic3d_NOM_STEEL))
    for n in range(5):
        a_trsf = gp_Trsf()
        a_trsf.SetTranslation(gp_Vec(n * 10, 0, 0))
        ais_box = AIS_Shape(box_shape)
        ais_box.SetLocalTransformation(a_trsf)
        ais_box.SetColor(Quantity_Color(Graphic3d_NOM_STEEL))
        gui.display(ais_box, True)
        test_list.append(ais_box)
    gui.v3d.FitAll()

    # gui.context.HilightSelected(False)
    # for ais in test_list:
    #     gui.context.Hilight(ais, True)
    # for ais in test_list:
    #     gui.context.UpdateSelected(True)
    #     print(gui.context.IsSelected(ais))
    # 显示 AIS_Shape
    # gui.display(ais_box, True)
    # gui.v3d.FitAll()
    # 设置高亮
    # gui.context.Hilight(ais_box, True)
    # 设置选中颜色
    selection_style = gui.context.SelectionStyle()
    selection_style.SetDisplayMode(1)
    selection_style.SetColor(getColor(13, 141, 255))
    # aHighlightStyle.PointAspect().SetTypeOfMarker(Aspect_TypeOfMarker.Aspect_TOM_PLUS)
    # aHighlightStyle.PointAspect().SetScale(3)
    selection_style.FaceBoundaryAspect().SetColor(getColor(0, 255, 0))
    # 设置选择
    gui.context.InitSelected()
    gui.context.AddSelect(test_list[2])
    print(gui.context.IsSelected(test_list[2]))
    # gui.context.Select(test_list[2],True)

    gui.context.UpdateSelected(True)
    gui.context.UpdateCurrentViewer()

    gui.context.ClearSelected(True)
    print(gui.context.IsSelected(test_list[2]))
    gui.context.UpdateSelected(True)
    gui.context.AddSelect(test_list[1])
    # gui.context.Select(test_list[2],True)

    gui.context.UpdateSelected(True)
    gui.context.UpdateCurrentViewer()

    # my_SelectMgr_EntityOwner = ais_box.GetOwner()
    # print(my_SelectMgr_EntityOwner)
    # gui.context.Selection().AddSelect(my_SelectMgr_EntityOwner)
    # gui.context.SetSelected(my_SelectMgr_EntityOwner, True)
    # xpmin, ypmin, xpmax, ypmax = 0, 0, 5000, 5000
    # gui.context.Select(xpmin, ypmin, xpmax, ypmax, gui.view, True)
    # gui.context.AddOrRemoveSelected(ais_box, True)
    # gui.context.ClearSelected()
    # print(gui.context.IsSelected(ais_box))
    # gui.context.UpdateSelected(True)
    # 选中高亮
    # gui.context.HilightSelected(False)
    # gui.update()


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
