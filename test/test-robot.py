from __future__ import annotations

import math
import sys

# logger
from loguru import logger

if sys.stderr:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
# pyOCC
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
    Graphic3d_TypeOfShadingModel,
    Graphic3d_Vec2i,
)
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Edge, TopoDS_Shape, TopoDS_Wire, topods
from OCC.Core.V3d import V3d_View
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool

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

# 赤橙黄绿青蓝紫灰八种颜色列表 (低饱和度版)
color_list = [
    (191, 32, 32),
    (191, 96, 32),
    (191, 191, 32),
    (32, 191, 32),
    (32, 191, 191),
    (32, 32, 191),
    (96, 32, 191),
    (128, 128, 128),
]


def getColor(r: int | tuple[int, int, int], g=0, b=0):
    """设置 OCC 颜色值

    Parameters
    ----------
    `r` : int | tuple[int, int, int]
        _description_
    `g` : int, optional
        _description_, by default 0
    `b` : int, optional
        _description_, by default 0

    Returns
    -------
    _type_
        _description_
    """
    if isinstance(r, tuple):
        r, g, b = r
    return Quantity_Color(r / float(255), g / float(255), b / float(255), Quantity_TOC_RGB)


# end def


def rotation_around_z(rotation_radius):
    """
    绕自身 Z 轴旋转
    """

    a_trsf = gp_Trsf()
    a_quat = gp_Quaternion()
    a_quat.SetVectorAndAngle(gp_Vec(0, 0, 1), rotation_radius)
    a_trsf.SetRotation(a_quat)
    return a_trsf


# end def


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
        """
        ========================================================================================
        TEST
        ========================================================================================
        """
        # 设置 pbr 阴影模式
        self.view.SetShadingModel(Graphic3d_TypeOfShadingModel.Graphic3d_TOSM_PBR)

        self.robot: MyRobot = None
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
    def update_robot(self, value):
        new_angles = [
            math.radians(self.slider_x.value()),
            math.radians(self.slider_y.value()),
            math.radians(self.slider_z.value()),
            math.radians(self.slider_w.value()),
            math.radians(self.slider_p.value()),
            math.radians(self.slider_r.value()),
        ]
        self.robot.update(new_angles, True)

    # end def
    def _create_right_layout(self):
        right_layout = QVBoxLayout()

        # create h layout
        sliders = QVBoxLayout()
        slider_wight_x, self.slider_x = create_slider(
            "Theta 1", 0, -180, 180, lambda x: x, self.update_robot
        )
        slider_wight_y, self.slider_y = create_slider(
            "Theta 2", -90, -180, 180, lambda x: x, self.update_robot
        )
        slider_wight_z, self.slider_z = create_slider(
            "Theta 3", 0, -180, 180, lambda x: x, self.update_robot
        )
        slider_wight_w, self.slider_w = create_slider(
            "Theta 4", 0, -180, 180, lambda x: x, self.update_robot
        )
        slider_wight_p, self.slider_p = create_slider(
            "Theta 5", 0, -180, 180, lambda x: x, self.update_robot
        )
        slider_wight_r, self.slider_r = create_slider(
            "Theta 6", 0, -180, 180, lambda x: x, self.update_robot
        )
        sliders.addWidget(slider_wight_x)
        sliders.addWidget(slider_wight_y)
        sliders.addWidget(slider_wight_z)
        sliders.addWidget(slider_wight_w)
        sliders.addWidget(slider_wight_p)
        sliders.addWidget(slider_wight_r)

        # 创建下拉选单
        self.comboBox = QComboBox(self)
        # self.comboBox.addItems(["AIS_" + str(i) for i in range(1, len(self.ais_list) + 1)])  # 将下拉选单项设置为 1, 2, 3, ...

        # create button
        # button = QPushButton("add tetrahedron")
        # button.clicked.connect(self.add_tetrahedron)

        # add
        right_layout.addWidget(self.comboBox)
        right_layout.addLayout(sliders)
        # right_layout.addWidget(button)
        return right_layout

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
def rotation_x(value):
    """
    Purpose:
    """
    quat = gp_Quaternion()
    quat.SetVectorAndAngle(gp_Vec(1, 0, 0), value)
    return quat


# end def
class MyRobot:
    def __init__(self, DH=None, other_input=None, base: gp_Trsf = gp_Trsf()):
        """
        Purpose: value
        """
        self.gui: MainWindow = None  # 不建议在创建机器人时设置显示窗口
        if DH:
            self.from_DH(DH)
        else:
            """
            ========================================================================================
            初始旋转角
            ========================================================================================
            """
            # todo 需要根据 DH 定义初始角度
            self.theta_1 = 0.0
            # self.theta_2 = math.radians(0)
            self.theta_2 = math.radians(-90)
            self.theta_3 = 0.0
            self.theta_4 = 0.0
            self.theta_5 = 0.0
            self.theta_6 = 0.0
            """
            ========================================================================================
            初始变换
            ========================================================================================
            """
            # todo 需要根据 DH 定义初始变换 (theta=0 时的变换)
            self._T0 = base  # 安装位置
            self._T01 = gp_Trsf()  # 从安装位置到 J1 的变换
            self._T01.SetTranslation(
                gp_Vec(0, 0, 460)
            )  # J1 轴安装时距离底座的高度，无法反应在 DH 中

            self._T12 = gp_Trsf()  # 从 J1 到 J2 的变换
            self._T12.SetTranslationPart(gp_Vec(320, 0, 0))
            self._T12.SetRotationPart(rotation_x(math.radians(-90)))

            self._T23 = gp_Trsf()  # 从 J2 到 J3 的变换
            self._T23.SetTranslationPart(gp_Vec(870, 0, 0))

            self._T34 = gp_Trsf()  # 从 J3 到 J4 的变换
            #! 实际显示上还需要额外走一个 Z=-1015 的平移
            self._T34.SetTranslationPart(gp_Vec(225, 0, 0))
            self._T34.SetRotationPart(rotation_x(math.radians(90)))

            self._T45 = gp_Trsf()  # 从 J4 到 J5 的变换
            #! 本来需要一个 z=-1015 的平移，在上一步做了
            # self._T45.SetTranslationPart(gp_Vec(0, 0, -1015))

            self._T45.SetRotationPart(rotation_x(math.radians(90)))
            self._T56 = gp_Trsf()  # 从 J5 到 J6 的变换
            #! 先旋转，后平移
            self._T56.SetRotationPart(rotation_x(math.radians(-90)))
            self._T6t = gp_Trsf()  # 从 J6 到手抓的变换
            self._T6t.SetRotationPart(rotation_x(math.radians(180)))
        # end if
        """
        ========================================================================================
        设置模型属性
        ========================================================================================
        """
        self._model_base = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/base.STEP")))
        self._model_J1 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J1.STEP")))
        self._model_J2 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J2.STEP")))
        self._model_J3 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J3.STEP")))
        self._model_J4 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J4.STEP")))
        self._model_J5 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J5.STEP")))
        self._model_J6 = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/J6.STEP")))
        self._model_tool = AIS_Shape_Tri(AIS_Shape(read_step("./robot-mods/tool.STEP")))
        # 设置颜色
        self._model_base.SetColor(getColor(color_list[0]))
        self._model_J1.SetColor(getColor(color_list[1]))
        self._model_J2.SetColor(getColor(color_list[2]))
        self._model_J3.SetColor(getColor(color_list[3]))
        self._model_J4.SetColor(getColor(color_list[4]))
        self._model_J5.SetColor(getColor(color_list[5]))
        self._model_J6.SetColor(getColor(color_list[6]))
        self._model_tool.SetColor(getColor(color_list[7]))
        # 设置透明度
        self._model_base.SetTransparency(0.6)
        self._model_J1.SetTransparency(0.6)
        self._model_J2.SetTransparency(0.6)
        self._model_J3.SetTransparency(0.6)
        self._model_J4.SetTransparency(0.6)
        self._model_J5.SetTransparency(0.6)
        self._model_J6.SetTransparency(0.6)
        self._model_tool.SetTransparency(0.6)

    # end alternate constructor

    # region 求正解
    """
    ========================================================================================
    求正解
    ========================================================================================
    """

    @property
    def T01(self):
        """
        从安装位置到 J1 的变换
        """
        # return self.base.Multiplied(rotation_around_z(math.radians(90))).Multiplied(self._T01)
        return self._T0.Multiplied(self._T01).Multiplied(rotation_around_z(self.theta_1))

    # end property
    @property
    def T12(self):
        """
        从 J1 到 J2 的变换
        """
        # return self.T01.Multiplied(rotation_around_z(0)).Multiplied(self._T12)
        return self._T12.Multiplied(rotation_around_z(self.theta_2))

    # end property
    @property
    def T23(self):
        """
        从 J2 到 J3 的变换
        """
        return self._T23.Multiplied(rotation_around_z(self.theta_3))

    # end property
    @property
    def T34(self):
        """
        从 J3 到 J4 的变换
        """
        #! 实际显示上还需要额外走一个 Z=-1015 的平移
        a_trsf = gp_Trsf()
        a_trsf.SetTranslation(gp_Vec(0, 0, -1015))
        return self._T34.Multiplied(rotation_around_z(self.theta_4)).Multiplied(a_trsf)

    # end property
    @property
    def T45(self):
        """
        从 J4 到 J5 的变换
        """
        return self._T45.Multiplied(rotation_around_z(self.theta_5))

    # end property
    @property
    def T56(self):
        """
        从 J5 到 J6 的变换
        """
        a_trsf = gp_Trsf()
        a_trsf.SetTranslation(gp_Vec(0, 0, -175))
        return self._T56.Multiplied(rotation_around_z(self.theta_6)).Multiplied(a_trsf)

    # end property
    @property
    def T6t(self):
        """
        从 J6 到 手抓 的变换
        """
        return self._T6t

    # end property
    @property
    def T02(self):
        """
        从安装位置到 J2 的变换
        """
        return self.T01.Multiplied(self.T12)

    # end property
    @property
    def T03(self):
        """
        从安装位置到 J3 的变换
        """
        return self.T02.Multiplied(self.T23)

    # end property
    @property
    def T04(self):
        """
        从安装位置到 J4 的变换
        """
        return self.T03.Multiplied(self.T34)

    # end property
    @property
    def T05(self):
        """
        从安装位置到 J5 的变换
        """
        return self.T04.Multiplied(self.T45)

    # end property
    @property
    def T06(self):
        """
        从安装位置到 J6 的变换
        """
        return self.T05.Multiplied(self.T56)

    # end property
    @property
    def T0t(self):
        """
        从安装位置到手抓的变换
        """
        return self.T06.Multiplied(self.T6t)

    # end property
    # endregion

    # region 模型实际显示的位置
    """
    ========================================================================================
    模型实际显示的位置
    ========================================================================================
    """

    @property
    def model_base(self):
        """
        实际显示的模型位置
        """
        self._model_base.SetLocalTransformation(self._T0)
        return self._model_base

    @property
    def model_J1(self):
        """
        实际显示的模型位置
        """
        self._model_J1.SetLocalTransformation(self.T01)
        return self._model_J1

    @property
    # end property
    def model_J2(self):
        """
        实际显示的模型位置
        """
        self._model_J2.SetLocalTransformation(self.T02)
        return self._model_J2

    # end property
    @property
    def model_J3(self):
        """
        实际显示的模型位置
        """
        self._model_J3.SetLocalTransformation(self.T03)
        return self._model_J3

    # end property
    @property
    def model_J4(self):
        """
        实际显示的模型位置
        """
        self._model_J4.SetLocalTransformation(self.T04)
        return self._model_J4

    # end property
    @property
    def model_J5(self):
        """
        实际显示的模型位置
        """
        self._model_J5.SetLocalTransformation(self.T05)
        return self._model_J5

    # end property
    @property
    def model_J6(self):
        """
        实际显示的模型位置
        """
        self._model_J6.SetLocalTransformation(self.T06)
        return self._model_J6

    # end property
    @property
    def model_tool(self):
        """
        实际显示的模型位置
        """
        self._model_tool.SetLocalTransformation(self.T0t)
        return self._model_tool

    # end property
    # endregion

    def from_DH(self, DH):
        """从 DH 表示生成机器人

        Parameters
        ----------
        DH : `_type_`, _description_
        """
        # todo 需要完成构建函数
        pass

    # end def
    def display(self, UPDATE_FLAG=False, gui: MainWindow = None):
        """
        Purpose:在 OCC 窗口展示机器人
        """
        if not self.gui:
            self.gui = gui
        self.gui.display(self.model_base, False)
        self.gui.display(self.model_J1, False)
        self.gui.display(self.model_J2, False)
        self.gui.display(self.model_J3, False)
        self.gui.display(self.model_J4, False)
        self.gui.display(self.model_J5, False)
        self.gui.display(self.model_J6, False)
        self.gui.display(self.model_tool, False)
        logger.info(
            f"""
J1  | {math.degrees(self.theta_1):.1f} 
J2  | {math.degrees(self.theta_2):.1f} 
J3  | {math.degrees(self.theta_3):.1f} 
J4  | {math.degrees(self.theta_4):.1f} 
J5  | {math.degrees(self.theta_5):.1f} 
J6  | {math.degrees(self.theta_6):.1f}
            """
        )
        if UPDATE_FLAG:
            self.gui.context.UpdateCurrentViewer()

    # end def
    def update(self, new_angles: list[float], UPDATE_FLAG=False):
        """更新机器人

        Parameters
        ----------
        `new_angles` : list[float]
            六个新的角度
        `UPDATE_FLAG` : bool, optional
            是否刷新视图，by default False
        """
        self.theta_1, self.theta_2, self.theta_3, self.theta_4, self.theta_5, self.theta_6 = (
            new_angles
        )
        self.display(UPDATE_FLAG=UPDATE_FLAG)

    # end def


# end class

"""
========================================================================================
测试代码
========================================================================================
"""


def test(gui: MainWindow):
    # fanuc_DH = None  # todo 输入实际的 DH，并完成 MyRobot 的 DH 解析函数
    # fanuc_robot = MyRobot()
    # # 显示
    # fanuc_robot.display(True, gui=gui)
    # 变换角度后显示
    # new_angles = [
    #     3.14,
    #     3.14,
    #     3.14,
    #     3.14,
    #     3.14,
    #     3.14,
    # ]
    # fanuc_robot.update(new_angles, True)
    agv_shape = read_step("./robot-mods/agv.STEP")
    agv_box = AIS_Shape_Tri(AIS_Shape(agv_shape), 1000)
    agv_box.SetColor(getColor(125, 125, 125))
    agv_box.SetTransparency(0.6)
    # a_trsf = gp_Trsf()
    # a_trsf.SetTranslation(gp_Vec(3, 2, 6))
    # ais_box.SetLocalTransformation(a_trsf)

    ais_tri_1 = AIS_Shape_Tri(arrow_length=500)
    a_trsf = gp_Trsf()
    a_trsf.SetRotationPart(gp_Quaternion(gp_Vec(0, 0, 1), 3.141592653))
    a_trsf.SetTranslationPart(gp_Vec(130.00, -355.00, 945.00))
    ais_tri_1.SetLocalTransformation(a_trsf)

    ais_tri_2 = AIS_Shape_Tri(arrow_length=500)
    robot_base_trsf = gp_Trsf()
    robot_base_trsf.SetTranslationPart(gp_Vec(-680.00, 450.00, 955.00))
    robot_base_trsf.SetRotationPart(gp_Quaternion(gp_Vec(1, 0, 0), gp_Vec(0, -1, 0)))
    ais_tri_2.SetLocalTransformation(robot_base_trsf)

    gui.robot = MyRobot(base=robot_base_trsf)
    gui.robot.display(True, gui=gui)

    gui.display(agv_box, False)
    gui.display(ais_tri_1, False)
    gui.display(ais_tri_2, False)
    # gui.v3d.default_drawer.SetColor(getColor(40, 40, 40))
    gui.v3d.default_drawer.SetColor(getColor(255, 0, 0))
    gui.v3d.FitAll()


# end def
"""
========================================================================================
创建窗口用于显示
========================================================================================
"""


def mainGUI():
    app = QApplication().instance()
    if not app:
        app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    gui.canvas.InitDriver()
    gui.canvas.qApp = app
    #!test
    test(gui)
    #!test
    # 窗口置顶
    gui.raise_()
    app.exec()


# end def
if __name__ == "__main__":
    mainGUI()
# end main
