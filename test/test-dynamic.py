import os
import random
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
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from pyOCC import create_tetrahedron, createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget

Dislpay = Callable[[AIS_InteractiveObject, bool], None]
from dynamic.transform import TransformMatrix_4x4


def NDArray2gp_Trsf(ndarray: TransformMatrix_4x4):
    trsf = gp_Trsf()
    trsf.SetValues(*ndarray.flatten()[:-4])
    return trsf


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
            origin_trihedron=True,
        )
        self.display = self.canvas.viewer3d.Context.Display
        self.context = self.canvas.viewer3d.Context
        self.view = self.canvas.viewer3d.View
        self.v3d = self.canvas.viewer3d
        self.centerOnScreen()
        """
        ========================================================================================
        TEST
        ========================================================================================
        """
        self._activated_light = []
        self.ambient_light = None
        self._create_right_layout()
        # 创建主布局，左侧 Canvas 占 3 部分，右侧按钮占 1 部分
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas, 3)
        main_layout.addLayout(self.right_layout, 1)

        # 创建主窗口的中心部件，并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # end alternate constructor
    def _create_right_layout(self):
        self.right_layout = QVBoxLayout()
        # DH参数表
        table_widget = QTableWidget()
        # 表格内容
        content = [
            ["320", "", "-90°", "theta_1", ""],
            ["870", "", "0", "theta_2", "-90°"],
            ["225", "", "90°", "theta_3", ""],
            ["", "-1015", "90°", "theta_4", ""],
            ["", "", "-90°", "theta_5", ""],
            ["", "-175", "180°", "theta_6", ""],
        ]
        table_widget.setRowCount(len(content))  # 行数
        table_widget.setColumnCount(len(content[0]))  # 列数
        # 表头
        headers = ["a", "d", "α", "θ", "offset"]
        table_widget.setHorizontalHeaderLabels(headers)
        for i, row in enumerate(content):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                table_widget.setItem(i, j, item)
        table_widget.resizeColumnsToContents()
        # 将表格添加到布局中
        self.right_layout.addWidget(table_widget)
        # DH参数表得到的矩阵
        a_v_layout = QVBoxLayout()
        self.right_layout.addLayout(a_v_layout)
        for i in range(3):
            sub_h_layout = QHBoxLayout()
            for j in range(4):
                text_edit = QLineEdit()
                sub_h_layout.addWidget(text_edit)
            a_v_layout.addLayout(sub_h_layout)

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


# end class
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    tetrahedron_shape = create_tetrahedron(10)
    tetrahedron_ais = AIS_Shape(tetrahedron_shape)
    tetrahedron_ais_tri = AIS_Shape_Tri(tetrahedron_ais)
    tetrahedron_ais_tri.SetColor(
        getColor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
    )
    gui.display(tetrahedron_ais_tri, True)
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
