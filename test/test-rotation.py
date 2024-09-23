import math
import os
import random
import sys
from functools import partial

from OCC.Core.AIS import (
    AIS_InteractiveContext,
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
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from pyOCC import create_tetrahedron, createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(
            self,
            origin_trihedron=True,
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
        """
        ========================================================================================
        TEST
        ========================================================================================
        """
        self.selected_ais: AIS_Shape = None
        self.ais_list: list[AIS_Shape] = []
        right_layout = self._create_right_layout()
        # 创建主布局，左侧 Canvas 占 3 部分，右侧按钮占 1 部分
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas, 3)
        main_layout.addLayout(right_layout, 1)

        # 创建主窗口的中心部件，并设置布局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # end alternate constructor
    def _create_right_layout(self):
        right_layout = QVBoxLayout()

        # create h layout
        sliders = QVBoxLayout()
        slider_wight_x, slider_x = create_slider("平移 X", 0, -100, 100, lambda x: x, self.t_x)
        slider_wight_y, slider_y = create_slider("平移 Y", 0, -100, 100, lambda x: x, self.t_y)
        slider_wight_z, slider_z = create_slider("平移 Z", 0, -100, 100, lambda x: x, self.t_z)
        slider_wight_w, slider_w = create_slider("旋转 W", 0, -180, 180, lambda x: x, self.t_w)
        slider_wight_p, slider_p = create_slider("旋转 P", 0, -180, 180, lambda x: x, self.t_p)
        slider_wight_r, slider_r = create_slider("旋转 R", 0, -180, 180, lambda x: x, self.t_r)
        sliders.addWidget(slider_wight_x)
        sliders.addWidget(slider_wight_y)
        sliders.addWidget(slider_wight_z)
        sliders.addWidget(slider_wight_w)
        sliders.addWidget(slider_wight_p)
        sliders.addWidget(slider_wight_r)

        # 创建下拉选单
        self.comboBox = QComboBox(self)
        # self.comboBox.addItems(["AIS_" + str(i) for i in range(1, len(self.ais_list) + 1)])  # 将下拉选单项设置为 1, 2, 3, ...

        def on_combobox_changed(index: int):
            self.selected_ais = self.ais_list[index]
            current_trsf = self.selected_ais.LocalTransformation()
            tp = current_trsf.TranslationPart()
            r, p, w = current_trsf.GetRotation().GetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX)
            slider_x.setValue(tp.X())
            slider_y.setValue(tp.Y())
            slider_z.setValue(tp.Z())
            slider_w.setValue(int(math.degrees(w)))
            slider_p.setValue(int(math.degrees(p)))
            slider_r.setValue(int(math.degrees(r)))

        self.comboBox.currentIndexChanged.connect(on_combobox_changed)

        # create button
        button = QPushButton("add tetrahedron")
        button.clicked.connect(self.add_tetrahedron)

        # add
        right_layout.addWidget(self.comboBox)
        right_layout.addLayout(sliders)
        right_layout.addWidget(button)
        return right_layout

    # end def
    def add_tetrahedron(self):
        tetrahedron_shape = create_tetrahedron(10)
        tetrahedron_ais = AIS_Shape(tetrahedron_shape)
        tetrahedron_ais_tri = AIS_Shape_Tri(tetrahedron_ais)
        tetrahedron_ais_tri.SetColor(
            getColor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
        )
        self.display(tetrahedron_ais_tri, True)
        self.ais_list.append(tetrahedron_ais_tri)
        self.comboBox.addItem(f"AIS_{len(self.ais_list)}", tetrahedron_ais_tri)
        self.v3d.FitAll()

    # end def
    def t_x(self, value):
        trsf = self.selected_ais.LocalTransformation()
        xyz = trsf.TranslationPart()
        xyz.SetX(value)
        trsf.SetTranslationPart(gp_Vec(xyz))
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

    # end def
    def t_y(self, value):
        trsf = self.selected_ais.LocalTransformation()
        xyz = trsf.TranslationPart()
        xyz.SetY(value)
        trsf.SetTranslationPart(gp_Vec(xyz))
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

    # end def
    def t_z(self, value):
        trsf = self.selected_ais.LocalTransformation()
        xyz = trsf.TranslationPart()
        xyz.SetZ(value)
        trsf.SetTranslationPart(gp_Vec(xyz))
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

    # end def
    def t_w(self, value):
        trsf = self.selected_ais.LocalTransformation()
        r, p, w = trsf.GetRotation().GetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX)
        quat = gp_Quaternion()
        quat.SetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX, r, p, math.radians(value))
        trsf.SetRotationPart(quat)
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

    # end def
    def t_p(self, value):
        trsf = self.selected_ais.LocalTransformation()
        r, p, w = trsf.GetRotation().GetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX)
        quat = gp_Quaternion()
        quat.SetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX, r, math.radians(value), w)
        trsf.SetRotationPart(quat)
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

    # end def
    def t_r(self, value):
        trsf = self.selected_ais.LocalTransformation()
        r, p, w = trsf.GetRotation().GetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX)
        quat = gp_Quaternion()
        quat.SetEulerAngles(gp_EulerSequence.gp_Extrinsic_ZYX, math.radians(value), p, w)
        trsf.SetRotationPart(quat)
        self.selected_ais.SetLocalTransformation(trsf)
        self.context.UpdateCurrentViewer()

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
def create_slider(
    label_name, init_value: int, min_value: int, max_value: int, real_value_calculator, fun
):
    slider_layout = QHBoxLayout()

    # button = QPushButton("ambient_light")
    # button.clicked.connect(partial(self.add_ambient_light, 1.0))

    # 创建 QLabel 用于显示滑条的值
    label = QLabel(f"{label_name}: {real_value_calculator(init_value)}")

    def _slider_value_changed(new_value):
        # 当滑条值改变时调用的函数
        real_value = real_value_calculator(new_value)  # 数值转为浮点数
        label.setText(f"{label_name}: {real_value}")
        if callable(fun):
            fun(real_value)

    # end def
    # 创建滑条
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)
    slider.setValue(init_value)  # 设置初始值
    slider.valueChanged.connect(_slider_value_changed)
    # add
    slider_layout.addWidget(label)
    slider_layout.addWidget(slider)
    # slider_layout.addWidget(button)

    slider_wight = QWidget()
    slider_wight.setLayout(slider_layout)

    return slider_wight, slider


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
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
