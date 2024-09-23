from __future__ import annotations

import copy
import math
import sys

import numpy as np

# logger
from loguru import logger

if sys.stderr:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
# pyOCC
from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_InteractiveObject,
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
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
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
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from pyOCC import create_tetrahedron, createTrihedron, getColor, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget


# 计算单位向量
def calUnitVector(vector):
    return vector / np.linalg.norm(vector)


def gp2np(Trsf):
    # 获取变换矩阵的元素并以矩阵形式打印
    matrix = np.array([[Trsf.Value(i, j) for j in range(1, 5)] for i in range(1, 4)])
    return matrix


# 把任意大小的弧度转换到-pi到pi的区间
def normRads(radians):
    normalized = math.fmod(radians, 2 * math.pi)
    if normalized > math.pi:
        normalized -= 2 * math.pi
    elif normalized < -math.pi:
        normalized += 2 * math.pi
    return normalized


def getTrsfDH(alpha, a, theta, d):
    trsf = gp_Trsf()
    trsf = trsf.Multiplied(getTrsfRotateX(alpha))
    trsf = trsf.Multiplied(getTrsfTranslateX(a))
    trsf = trsf.Multiplied(getTrsfRotateZ(theta))
    trsf = trsf.Multiplied(getTrsfTranslateZ(d))
    return trsf


def getTrsfTranslateX(distance):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(distance, 0, 0))
    return trsf


def getTrsfTranslateY(distance):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, distance, 0))
    return trsf


def getTrsfTranslateZ(distance):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(0, 0, distance))
    return trsf


def getTrsfRotateZ(rotationRadius):
    trsf = gp_Trsf()
    quat = gp_Quaternion()
    quat.SetVectorAndAngle(gp_Vec(0, 0, 1), rotationRadius)
    trsf.SetRotation(quat)
    return trsf


def getTrsfRotateY(rotationRadius):
    trsf = gp_Trsf()
    quat = gp_Quaternion()
    quat.SetVectorAndAngle(gp_Vec(0, 1, 0), rotationRadius)
    trsf.SetRotation(quat)
    return trsf


def getTrsfRotateX(rotationRadius):
    trsf = gp_Trsf()
    quat = gp_Quaternion()
    quat.SetVectorAndAngle(gp_Vec(1, 0, 0), rotationRadius)
    trsf.SetRotation(quat)
    return trsf


def createSlider(
    labelName,
    initValue: int,
    minValue: int,
    maxValue: int,
    changeDisplayFormat,
    updateFun,
):
    def sliderValueChanged(newValue):
        # 当滑条值改变时调用的函数
        realValue = changeDisplayFormat(newValue)  # 按要求修改数值显示格式
        thetaValue.setText(f"{realValue}")
        thetaValue.setFont(font)
        if callable(updateFun):
            updateFun()

    # 等宽字体格式
    font = QFont("Courier", 10)
    # 组装布局
    # theta名字
    sliderLayout = QHBoxLayout()
    thetaName = QLabel(f"{labelName}:(")
    thetaName.setFont(font)
    sliderLayout.addWidget(thetaName)
    # theta值
    thetaValue = QLabel(f"{initValue:>4}")
    thetaValue.setObjectName("thetaValue")
    thetaValue.setFont(font)
    sliderLayout.addWidget(thetaValue)
    # theta最小值
    thetaMinValue = QLabel(f"){minValue}")
    thetaMinValue.setFont(font)
    sliderLayout.addWidget(thetaMinValue)
    # 滑动条本体
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(initValue)  # 设置初始值
    slider.setMinimum(minValue)
    slider.setMaximum(maxValue)
    slider.valueChanged.connect(sliderValueChanged)
    sliderLayout.addWidget(slider)
    # theta最大值
    thetaMaxValue = QLabel(f"{maxValue}")
    thetaMaxValue.setFont(font)
    sliderLayout.addWidget(thetaMaxValue)
    # 组装 Wight
    sliderWight = QWidget()
    sliderWight.setLayout(sliderLayout)
    return sliderWight, slider


class SixAxisRobot:
    def __init__(
        self,
        modList=None,
        DH=None,
        DH_6t=None,
        isSameDirection=None,
        initRad=None,
    ):
        self.DH = DH
        self.DH_6t = DH_6t
        self.isSameDirection = isSameDirection
        self.initRad = initRad
        # 导入模型
        self._model_0 = AIS_Shape_Tri(AIS_Shape(read_step(modList[0])))
        self._model_1 = AIS_Shape_Tri(AIS_Shape(read_step(modList[1])))
        self._model_2 = AIS_Shape_Tri(AIS_Shape(read_step(modList[2])))
        self._model_3 = AIS_Shape_Tri(AIS_Shape(read_step(modList[3])))
        self._model_4 = AIS_Shape_Tri(AIS_Shape(read_step(modList[4])))
        self._model_5 = AIS_Shape_Tri(AIS_Shape(read_step(modList[5])))
        self._model_6 = AIS_Shape_Tri(AIS_Shape(read_step(modList[6])))
        new_trsf = gp_Trsf()
        new_trsf.SetTranslation(gp_Vec(-30, 0, -230))
        tool_shape = BRepBuilderAPI_Transform(read_step(modList[7]), new_trsf).Shape()
        self._model_t = AIS_Shape_Tri(AIS_Shape(tool_shape))

    # J0 to J1
    @property
    def T_01(self):
        return getTrsfDH(
            self.DH["alpha"][0],
            self.DH["a"][0],
            self.DH["thetaOffset"][0] + self.DH["thetaCurrent"][0],
            self.DH["d"][0],
        )

    # J1 to J2
    @property
    def T_12(self):
        return getTrsfDH(
            self.DH["alpha"][1],
            self.DH["a"][1],
            self.DH["thetaOffset"][1] + self.DH["thetaCurrent"][1],
            self.DH["d"][1],
        )

    # J2 to J3
    @property
    def T_23(self):
        return getTrsfDH(
            self.DH["alpha"][2],
            self.DH["a"][2],
            self.DH["thetaOffset"][2] + self.DH["thetaCurrent"][2],
            self.DH["d"][2],
        )

    # J3 to J4
    @property
    def T_34(self):
        return getTrsfDH(
            self.DH["alpha"][3],
            self.DH["a"][3],
            self.DH["thetaOffset"][3] + self.DH["thetaCurrent"][3],
            self.DH["d"][3],
        )

    # J4 to J5
    @property
    def T_45(self):
        return getTrsfDH(
            self.DH["alpha"][4],
            self.DH["a"][4],
            self.DH["thetaOffset"][4] + self.DH["thetaCurrent"][4],
            self.DH["d"][4],
        )

    # J5 to J6
    @property
    def T_56(self):
        return getTrsfDH(
            self.DH["alpha"][5],
            self.DH["a"][5],
            self.DH["thetaOffset"][5] + self.DH["thetaCurrent"][5],
            self.DH["d"][5],
        )

    # J6 to Jt
    @property
    def T_6t(self):
        return getTrsfDH(
            self.DH_6t["alpha"], self.DH_6t["a"], self.DH_6t["thetaOffset"], self.DH_6t["d"]
        )

    @property
    def T_02(self):
        return self.T_01.Multiplied(self.T_12)

    @property
    def T_03(self):
        return self.T_02.Multiplied(self.T_23)

    @property
    def T_04(self):
        return self.T_03.Multiplied(self.T_34)

    @property
    def T_05(self):
        return self.T_04.Multiplied(self.T_45)

    @property
    def T_06(self):
        return self.T_05.Multiplied(self.T_56)

    @property
    def T_0t(self):
        return self.T_06.Multiplied(self.T_6t)

    @property
    def model_0(self):
        """实际显示的模型位置"""
        _model0 = gp_Trsf()
        return self._model_0

    @property
    def model_1(self):
        """实际显示的模型位置"""
        self._model_1.SetLocalTransformation(self.T_01)
        return self._model_1

    @property
    def model_2(self):
        """实际显示的模型位置"""
        self._model_2.SetLocalTransformation(self.T_02)
        return self._model_2

    @property
    def model_3(self):
        """实际显示的模型位置"""
        self._model_3.SetLocalTransformation(self.T_03)
        return self._model_3

    @property
    def model_4(self):
        """实际显示的模型位置"""
        self._model_4.SetLocalTransformation(self.T_04)
        return self._model_4

    @property
    def model_5(self):
        """实际显示的模型位置"""
        self._model_5.SetLocalTransformation(self.T_05)
        return self._model_5

    @property
    def model_6(self):
        """实际显示的模型位置"""
        self._model_6.SetLocalTransformation(self.T_06)
        return self._model_6

    @property
    def model_t(self):
        """实际显示的模型位置"""
        self._model_t.SetLocalTransformation(self.T_0t)
        return self._model_t


class RobotWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 主窗口和布局
        screenSize = QGuiApplication.primaryScreen().availableGeometry()
        self.setFixedSize(0.8 * screenSize.width(), 0.8 * screenSize.height())
        self.setWindowTitle("机器人 Demo")
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        topLevelLayout = QHBoxLayout(centralWidget)

        # 左侧 (三维画布)
        self.canvas = qtViewer3dWidget(self)
        topLevelLayout.addWidget(self.canvas, 3)
        self.display = self.canvas.viewer3d.Context.Display
        self.context = self.canvas.viewer3d.Context
        self.view = self.canvas.viewer3d.View
        self.v3d = self.canvas.viewer3d
        # 渐变色背景
        self.view.SetBgGradientColors(
            getColor(40, 40, 40),
            getColor(170, 170, 170),
            Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
            True,
        )
        self.view.SetBgGradientColors(
            getColor(37, 55, 113),
            getColor(36, 151, 132),
            Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
            True,
        )
        self.canvas.viewer3d.EnableAntiAliasing()  # 开启抗锯齿
        self.view.SetShadingModel(Graphic3d_TypeOfShadingModel.Graphic3d_TOSM_PBR)  # 设置着色器

        # 右侧（机器人控制界面）
        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 400)  # 设置右侧布局的边距
        topLevelLayout.addLayout(rightLayout, 1)  # 右侧占比 1/4 的空间

        # 参考坐标系标签和输入行
        rightLayout.addWidget(QLabel("<b>参考坐标系</b>"))
        self.refCoords = {}
        refCoordsLayout = QHBoxLayout()
        for axis in ["Px", "Py", "Pz", "Rz", "Ry'", "Rx''"]:
            refCoordsLayout.addWidget(QLabel(axis))
            lineEdit = QLineEdit("0")
            self.refCoords[axis] = lineEdit
            lineEdit.setReadOnly(True)
            refCoordsLayout.addWidget(lineEdit)
        rightLayout.addLayout(refCoordsLayout)

        # 工具坐标系标签和输入行
        rightLayout.addWidget(QLabel("<b>工具坐标系相对于参考坐标系</b>"))
        self.toolCoords = {}
        toolCoordsLayout = QHBoxLayout()
        for axis in ["Px", "Py", "Pz", "Rz", "Ry'", "Rx''"]:
            toolCoordsLayout.addWidget(QLabel(axis))
            lineEdit = QLineEdit()
            self.toolCoords[axis] = lineEdit
            toolCoordsLayout.addWidget(lineEdit)
        rightLayout.addLayout(toolCoordsLayout)

        # 其他构型
        rightLayout.addWidget(QLabel("<b>其他位姿 (θ1, θ2, θ3, θ4, θ5, θ6)</b>"))
        configsLayout = QHBoxLayout()
        self.otherPoses = np.zeros((8, 6))
        self.otherPosesLabel = QComboBox()
        for i in range(8):
            self.otherPosesLabel.addItem(f"θ1=0, θ2=0, θ3=0, θ4=0, θ5=0, θ6=0")
        configsLayout.addWidget(self.otherPosesLabel, 4)
        self.otherPosesLabel.currentIndexChanged.connect(self.updatePose)
        # 逆解部分
        inverseButton = QPushButton("求逆解")
        inverseButton.clicked.connect(self.solveInverseKinematics)
        configsLayout.addWidget(inverseButton, 1)
        rightLayout.addLayout(configsLayout)

        # 关节轴转动标签和滑块
        rightLayout.addWidget(QLabel("<b>关节轴转动</b>"))
        slidersLayout = QVBoxLayout()
        rightLayout.addLayout(slidersLayout)
        self.sliderWight1, self.slider1 = createSlider(
            "θ1", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        self.sliderWight2, self.slider2 = createSlider(
            "θ2", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        self.sliderWight3, self.slider3 = createSlider(
            "θ3", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        self.sliderWight4, self.slider4 = createSlider(
            "θ4", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        self.sliderWight5, self.slider5 = createSlider(
            "θ5", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        self.sliderWight6, self.slider6 = createSlider(
            "θ6", 0, -180, 180, lambda x: f"{x:>4}", self.updateWindow
        )
        slidersLayout.addWidget(self.sliderWight1)
        slidersLayout.addWidget(self.sliderWight2)
        slidersLayout.addWidget(self.sliderWight3)
        slidersLayout.addWidget(self.sliderWight4)
        slidersLayout.addWidget(self.sliderWight5)
        slidersLayout.addWidget(self.sliderWight6)
        # 复位按钮
        resetButton = QPushButton("复位")
        resetButton.clicked.connect(self.reset)
        rightLayout.addWidget(resetButton)

        # ! 显示机器人
        self.test_robot()

    def test_robot(self):
        # 机器人模型
        modList = [
            "./robot-mods/J0.STEP",
            "./robot-mods/J1.STEP",
            "./robot-mods/J2.STEP",
            "./robot-mods/J3.STEP",
            "./robot-mods/J4.STEP",
            "./robot-mods/J5.STEP",
            "./robot-mods/J6.STEP",
            "./robot-mods/Jt.STEP",
        ]
        DH = {
            "alpha": [
                math.radians(0),
                math.radians(-90),
                math.radians(0),
                math.radians(90),
                math.radians(90),
                math.radians(-90),
            ],
            "a": [0, 320, 870, 225, 0, 0],
            "thetaOffset": [
                math.radians(0),
                math.radians(-90),
                math.radians(0),
                math.radians(0),
                math.radians(0),
                math.radians(0),
            ],
            "thetaCurrent": [0, 0, 0, 0, 0, 0],
            "d": [490, 0, 0, -1015, 0, -175],
        }
        DH_6t = {
            "alpha": math.radians(180),
            "a": 0,
            "thetaOffset": math.radians(0),
            "d": 230,
        }
        # 第二和第三个z轴指向是否和规定的坐标系相同
        isSameDirection = [False, False]
        # 前三个轴从既定姿态到初始姿态要转的角度（以自身旋转角度的方向为正）
        initRad = [math.radians(0), math.radians(90), math.radians(-90)]
        self.robot = SixAxisRobot(modList, DH, DH_6t, isSameDirection, initRad)
        self.updateRobot()
        self.updateCoords()

    def updateWindow(self):
        # 更新角度
        self.robot.DH["thetaCurrent"] = [
            math.radians(self.slider1.value()),
            math.radians(self.slider2.value()),
            math.radians(self.slider3.value()),
            math.radians(self.slider4.value()),
            math.radians(self.slider5.value()),
            math.radians(self.slider6.value()),
            math.radians(0),
        ]
        # 更新左侧显示
        self.updateRobot()
        # 更新右侧坐标系显示
        self.updateCoords()

    # 更新机器人显示
    def updateRobot(self):
        self.display(self.robot.model_0, False)
        self.display(self.robot.model_1, False)
        self.display(self.robot.model_2, False)
        self.display(self.robot.model_3, False)
        self.display(self.robot.model_4, False)
        self.display(self.robot.model_5, False)
        self.display(self.robot.model_6, False)
        self.display(self.robot.model_t, False)
        self.context.UpdateCurrentViewer()

    def updatePose(self, index):
        self.updateSlider(self.otherPoses[index])
        # 更新角度
        self.robot.DH["thetaCurrent"] = [
            self.otherPoses[index][0],
            self.otherPoses[index][1],
            self.otherPoses[index][2],
            self.otherPoses[index][3],
            self.otherPoses[index][4],
            self.otherPoses[index][5],
            math.radians(0),
        ]
        # 更新左侧显示
        self.updateRobot()
        # 更新右侧坐标系显示
        self.updateCoords()

    # 更新坐标系显示
    def updateCoords(self):
        self.toolCoords["Px"].setText(f"{self.robot.T_0t.TranslationPart().X():.0f}")
        self.toolCoords["Py"].setText(f"{self.robot.T_0t.TranslationPart().Y():.0f}")
        self.toolCoords["Pz"].setText(f"{self.robot.T_0t.TranslationPart().Z():.0f}")
        quaternion = self.robot.T_0t.GetRotation()
        angles = quaternion.GetEulerAngles(gp_EulerSequence.gp_Intrinsic_ZYX)
        self.toolCoords["Rz"].setText(f"{math.degrees(angles[0]):.0f}")
        self.toolCoords["Ry'"].setText(f"{math.degrees(angles[1]):.0f}")
        self.toolCoords["Rx''"].setText(f"{math.degrees(angles[2]):.0f}")

    def updateSlider(self, thetaList):
        # 等宽字体格式
        font = QFont("Courier", 10)
        # 修改滑块标签的值
        thetaValue = self.sliderWight1.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[0])):>4}")
        thetaValue.setFont(font)
        thetaValue = self.sliderWight2.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[1])):>4}")
        thetaValue.setFont(font)
        thetaValue = self.sliderWight3.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[2])):>4}")
        thetaValue.setFont(font)
        thetaValue = self.sliderWight4.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[3])):>4}")
        thetaValue.setFont(font)
        thetaValue = self.sliderWight5.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[4])):>4}")
        thetaValue.setFont(font)
        thetaValue = self.sliderWight6.findChild(QLabel, "thetaValue")
        thetaValue.setText(f"{int(math.degrees(thetaList[5])):>4}")
        thetaValue.setFont(font)
        # 修改滑块的值
        self.slider1.blockSignals(True)
        self.slider2.blockSignals(True)
        self.slider3.blockSignals(True)
        self.slider4.blockSignals(True)
        self.slider5.blockSignals(True)
        self.slider6.blockSignals(True)
        self.slider1.setValue(math.degrees(thetaList[0]))
        self.slider2.setValue(math.degrees(thetaList[1]))
        self.slider3.setValue(math.degrees(thetaList[2]))
        self.slider4.setValue(math.degrees(thetaList[3]))
        self.slider5.setValue(math.degrees(thetaList[4]))
        self.slider6.setValue(math.degrees(thetaList[5]))
        self.slider1.blockSignals(False)
        self.slider2.blockSignals(False)
        self.slider3.blockSignals(False)
        self.slider4.blockSignals(False)
        self.slider5.blockSignals(False)
        self.slider6.blockSignals(False)

    # 复位
    def reset(self):
        self.updateSlider([0, 0, 0, 0, 0, 0, 0])
        self.updateWindow()

    # 求逆解
    def solveInverseKinematics(self):
        """=====================输入参数====================="""
        # 工具坐标系相对于参考坐标系的位姿, 用于形成其次变换矩阵, Dof和T_0t输入其一
        # Dof = [self.toolCoords["Px"].text(),
        #        self.toolCoords["Py"].text(),
        #        self.toolCoords["Pz"].text(),
        #        self.toolCoords["Rz"].text(),
        #        self.toolCoords["Ry'"].text(),
        #        self.toolCoords["Rx''"].text()]
        # T_0t = gp_Trsf()
        # T_0t = T_0t.Multiplied(translate_x(float(Dof[0])))
        # T_0t = T_0t.Multiplied(translate_y(float(Dof[1])))
        # T_0t = T_0t.Multiplied(translate_z(float(Dof[2])))
        # T_0t = T_0t.Multiplied(rotation_z(math.radians(float(Dof[3]))))
        # T_0t = T_0t.Multiplied(rotation_y(math.radians(float(Dof[4]))))
        # T_0t = T_0t.Multiplied(rotation_x(math.radians(float(Dof[5]))))
        T_0t = self.robot.T_0t
        # J6 to Jt 的其次变换矩阵
        T_6t_gp = copy.deepcopy(self.robot.T_6t)
        # DH参数
        DH = copy.deepcopy(self.robot.DH)
        # 初始位姿到既定位姿的其次变换矩阵列表
        isSameDirection = copy.deepcopy(self.robot.isSameDirection)

        """=====================函数主体(求逆变换)====================="""
        """
        注意：计算theta 2 3 时,是通过机器人的形状确定坐标系，在其中计算，因此需要坐标系转换
        z轴：沿着J1主轴方向，指向向上
        x轴：沿着J2臂长的方向，指向J3，且垂直于z轴
        y轴：右手定则确定
        theta角以让臂向上转动的趋势为正
        alpha 默认为正
        """
        # 初始化 待求角度
        otherPoses = np.zeros((8, 6))
        # 计算 J0 to J6 的其次变换矩阵
        T_06_gp = T_0t.Multiplied(T_6t_gp.Inverted())
        T_06_np = gp2np(T_06_gp)
        # 计算 J5 相对于 J1 的坐标
        x5, y5, z5 = T_06_np[:3, 3].T - DH["d"][5] * calUnitVector(T_06_np[:3, 2])
        # 计算theta 1 [正手，反手]
        theta_1 = [math.atan2(y5, x5), math.atan2(y5, x5) + math.pi]
        # 组装
        otherPoses[0:4, 0] = theta_1[0]
        otherPoses[4:8, 0] = theta_1[1]
        # 计算theta 2 3 的前置步骤
        # 在既定位姿和坐标系下计算，J1=>J2的方向为x正方向, J1的z轴为z正方向（默认上方）
        theta_3a = np.zeros(2)  # theta_3+alpha
        # 杆长
        a0 = DH["d"][0]  # 基座到第一个坐标系的长度
        a1 = DH["a"][1]  # J1 长
        a2 = DH["a"][2]  # J2 长
        a3 = math.sqrt(DH["a"][3] ** 2 + DH["d"][3] ** 2)  # J3 长
        alpha = math.atan(abs(DH["a"][3] / DH["d"][3]))  # J3 形状自带的夹角(默认J3是向上凸起)
        # J5相对于J1的x z
        ex_dash = np.zeros(2)
        ez_dash = np.zeros(2)
        gamma = np.zeros(2)  # J5在J1坐标系下与XOY平面的夹角
        beta = np.zeros(2)  # J3-J1-J2的夹角
        # 计算 ex_dash ez_dash (矢量)
        for i in range(2):
            ex_dash[i] = x5 / math.cos(theta_1[i]) - a1
            ez_dash[i] = z5 - a0
        # 计算 theta_3a (标量)
        for i in range(2):
            cos_3a = (ex_dash[i] ** 2 + ez_dash[i] ** 2 - (a2**2 + a3**2)) / (2 * a2 * a3)
            if cos_3a < -1 or cos_3a > 1:
                theta_3a[i] = np.nan
                continue
            else:
                theta_3a[i] = math.acos(cos_3a)
        # 计算 gamma (矢量) beta (标量)
        for i in range(2):
            gamma[i] = math.atan2(ez_dash[i], ex_dash[i])
            beta[i] = math.atan2(a3 * math.sin(theta_3a[i]), a2 + a3 * math.cos(theta_3a[i]))
        # 组装(在规定姿态下的theta, 注意正手反手下求得的角度是顺时针or逆时针)
        otherPoses[0:2, 1:3] = gamma[0] - beta[0], theta_3a[0] - alpha
        otherPoses[2:4, 1:3] = gamma[0] + beta[0], -theta_3a[0] - alpha
        otherPoses[4:6, 1:3] = gamma[1] + beta[1], -(theta_3a[1] + alpha)
        otherPoses[6:8, 1:3] = gamma[1] - beta[1], -(-theta_3a[1] + alpha)
        # 恢复到实际角度
        otherPoses[:, 1] = (
            float(2 * isSameDirection[0] - 1) * otherPoses[:, 1] + self.robot.initRad[1]
        )
        otherPoses[:, 2] = (
            float(2 * isSameDirection[1] - 1) * otherPoses[:, 2] + self.robot.initRad[2]
        )
        # 计算theta 4 5 6
        # 默认 alpha 3 4 5 为90度或-90度
        for i in range(0, 8, 2):
            T01_gp = getTrsfDH(
                DH["alpha"][0], DH["a"][0], otherPoses[i, 0] + DH["thetaOffset"][0], DH["d"][0]
            )
            T12_gp = getTrsfDH(
                DH["alpha"][1], DH["a"][1], otherPoses[i, 1] + DH["thetaOffset"][1], DH["d"][1]
            )
            T23_gp = getTrsfDH(
                DH["alpha"][2], DH["a"][2], otherPoses[i, 2] + DH["thetaOffset"][2], DH["d"][2]
            )
            T03_gp = T01_gp.Multiplied(T12_gp).Multiplied(T23_gp)
            T36_gp = T03_gp.Inverted().Multiplied(T_06_gp)
            q13 = T36_gp.Value(1, 3)
            q23 = T36_gp.Value(2, 3)
            q33 = T36_gp.Value(3, 3)
            q21 = T36_gp.Value(2, 1)
            q22 = T36_gp.Value(2, 2)

            c4s5 = q13 / math.sin(DH["alpha"][5])
            c5 = q23 / (
                math.sin(DH["alpha"][3]) * math.sin(DH["alpha"][4]) * math.sin(DH["alpha"][5])
            )
            s4s5 = q33 / (math.sin(DH["alpha"][3]) * math.sin(DH["alpha"][5]))
            s5c6 = -q21 / (math.sin(DH["alpha"][3]) * math.sin(DH["alpha"][4]))
            s5s6 = q22 / (math.sin(DH["alpha"][3]) * math.sin(DH["alpha"][4]))

            otherPoses[i, 3] = math.atan2(s4s5, c4s5)
            otherPoses[i + 1, 3] = otherPoses[i, 3] + math.pi
            otherPoses[i, 4] = math.atan2(math.sqrt(c4s5**2 + s4s5**2), c5)
            otherPoses[i + 1, 4] = -otherPoses[i, 4]
            otherPoses[i, 5] = math.atan2(s5s6, s5c6)
            otherPoses[i + 1, 5] = otherPoses[i, 5] + math.pi

        """=====================存储到其他构型中====================="""
        # 去除nan行
        otherPoses = otherPoses[~np.isnan(otherPoses).any(axis=1)]
        # 角度标准化
        vecNormRads = np.vectorize(normRads)
        otherPoses = vecNormRads(otherPoses)
        self.otherPoses = otherPoses
        self.otherPosesLabel.blockSignals(True)
        self.otherPosesLabel.clear()  # 清除现有的项
        for Pose in self.otherPoses:
            item_text = (
                f"θ1={int(math.degrees(Pose[0]))}, θ2={int(math.degrees(Pose[1]))}, "
                f"θ3={int(math.degrees(Pose[2]))}, θ4={int(math.degrees(Pose[3]))}, "
                f"θ5={int(math.degrees(Pose[4]))}, θ6={int(math.degrees(Pose[5]))}"
            )
            self.otherPosesLabel.addItem(item_text)
        self.otherPosesLabel.blockSignals(False)


if __name__ == "__main__":
    app = QApplication([])
    demo = RobotWindow()
    demo.show()
    app.exec()
