import math
import sys

from loguru import logger

if sys.stderr:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")

from OCC.Core.AIS import AIS_Shape
from OCC.Core.Aspect import Aspect_GradientFillMethod
from OCC.Core.gp import gp_EulerSequence, gp_Quaternion, gp_Trsf, gp_Vec

# PySide6
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow

# local
from qtViewer3d import qtViewer3dWidget


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


def rotation_around_z(rotation_radius=None, rotation_degree=None):
    """
    绕自身 Z 轴旋转
    """

    def _rot(r_radius):
        a_trsf = gp_Trsf()
        a_quat = gp_Quaternion()
        a_quat.SetEulerAngles(gp_EulerSequence.gp_Intrinsic_XYZ, 0, 0, r_radius)
        a_trsf.SetRotation(a_quat)
        return a_trsf

    # end def
    if rotation_radius:
        return _rot(rotation_radius)
    elif rotation_degree:
        return _rot(math.radians(rotation_degree))
    else:
        raise ValueError("请输入旋转值")
    # end if


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
            getColor(37, 55, 113), getColor(36, 151, 132), Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical, True
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
class MyRobot:
    def __init__(self, install_hight: int, DH=None, other_input=None):
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
            self.theta_2 = 0.0
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
            self.base = gp_Trsf()  # 安装位置
            self._T01 = gp_Trsf()  # 从安装位置到 J1 的变换
            self._T01.SetTranslation(gp_Vec(0, 0, install_hight))  # J1 轴安装时距离底座的高度，无法反应在 DH 中
            self._T12 = gp_Trsf()  # 从 J1 到 J2 的变换
            self._T23 = gp_Trsf()  # 从 J2 到 J3 的变换
            self._T34 = gp_Trsf()  # 从 J3 到 J4 的变换
            self._T45 = gp_Trsf()  # 从 J4 到 J5 的变换
            self._T56 = gp_Trsf()  # 从 J5 到 J6 的变换
            self._T6t = gp_Trsf()  # 从 J6 到手抓的变换
        # end if
        """
        ========================================================================================
        显示模型
        ========================================================================================
        """
        # todo 需要完成用于显示模型的构建
        self.model_J1: AIS_Shape = None
        self._model_J2: AIS_Shape = None
        self._model_J3: AIS_Shape = None
        self._model_J4: AIS_Shape = None
        self._model_J5: AIS_Shape = None
        self._model_J6: AIS_Shape = None
        self._model_tool: AIS_Shape = None

    # end alternate constructor
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
        return self._T01

    # end property
    @property
    def T12(self):
        """
        从 J1 到 J2 的变换
        """
        return self._T01.Multiplied(rotation_around_z(self.theta_1)).Multiplied(self._T12)

    # end property
    @property
    def T23(self):
        """
        从 J2 到 J3 的变换
        """
        return self.T02.Multiplied(rotation_around_z(self.theta_2)).Multiplied(self._T23)

    # end property
    @property
    def T34(self):
        """
        从 J3 到 J4 的变换
        """
        return self.T03.Multiplied(rotation_around_z(self.theta_3)).Multiplied(self._T34)

    # end property
    @property
    def T45(self):
        """
        从 J4 到 J5 的变换
        """
        return self.T04.Multiplied(rotation_around_z(self.theta_4)).Multiplied(self._T45)

    # end property
    @property
    def T56(self):
        """
        从 J5 到 J6 的变换
        """
        return self.T05.Multiplied(rotation_around_z(self.theta_5)).Multiplied(self._T56)

    # end property
    @property
    def T6t(self):
        """
        从 J6 到 手抓 的变换
        """
        return self.T06.Multiplied(rotation_around_z(self.theta_6)).Multiplied(self._T6t)

    # end property
    @property
    def T02(self):
        """
        从安装位置到 J2 的变换
        """
        return self.base.Multiplied(self.T12)

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
    """
    ========================================================================================
    模型实际显示的位置
    ========================================================================================
    """

    def model_J2(self):
        """
        实际显示的模型位置
        """
        self._model_J2.SetLocalTransformation(self.T01)
        return self._model_J2

    # end property
    def model_J3(self):
        """
        实际显示的模型位置
        """
        self._model_J3.SetLocalTransformation(self.T02)
        return self._model_J3

    # end property
    def model_J4(self):
        """
        实际显示的模型位置
        """
        self._model_J4.SetLocalTransformation(self.T03)
        return self._model_J4

    # end property
    def model_J5(self):
        """
        实际显示的模型位置
        """
        self._model_J5.SetLocalTransformation(self.T04)
        return self._model_J5

    # end property
    def model_J6(self):
        """
        实际显示的模型位置
        """
        self._model_J6.SetLocalTransformation(self.T05)
        return self._model_J6

    # end property
    def model_tool(self):
        """
        实际显示的模型位置
        """
        self._model_tool.SetLocalTransformation(self.T06)
        return self._model_tool

    # end property
    def from_DH(self, DH):
        """从 DH 坐标中构建机器人

        Parameters
        ----------
        `DH` : _type_
            _description_
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
        gui.display(self.model_J1, False)
        gui.display(self.model_J2, False)
        gui.display(self.model_J3, False)
        gui.display(self.model_J4, False)
        gui.display(self.model_J5, False)
        gui.display(self.model_J6, False)
        gui.display(self.model_tool, False)
        logger.info(f"当前角度:\n{self.theta_1},{self.theta_2},{self.theta_3},{self.theta_4},{self.theta_5},{self.theta_6}")
        if UPDATE_FLAG:
            gui.context.UpdateCurrentViewer()

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
        self.theta_1, self.theta_2, self.theta_3, self.theta_4, self.theta_5, self.theta_6 = new_angles
        self.display(UPDATE_FLAG=UPDATE_FLAG)

    # end def


# end class

"""
========================================================================================
测试代码
========================================================================================
"""


def test(gui: MainWindow):
    fanuc_DH = None  # todo 输入实际的 DH，并完成 MyRobot 的 DH 解析函数
    fanuc_robot = MyRobot(install_hight=500, DH=fanuc_DH)
    # 显示
    fanuc_robot.display(True, gui=gui)
    # 变换角度后显示
    new_angles = [
        3.14,
        3.14,
        3.14,
        3.14,
        3.14,
        3.14,
    ]
    fanuc_robot.update(new_angles, True)
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
