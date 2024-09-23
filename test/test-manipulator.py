import os
import sys
from functools import partial
from typing import Callable

from context import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidgetManipulator()
        self.display = self.canvas.viewer3d.Context.Display
        self.context = self.canvas.viewer3d.Context
        self.view = self.canvas.viewer3d.View
        self.viewer = self.canvas.viewer3d.Viewer
        self.v3d = self.canvas.viewer3d
        # self.setCentralWidget(self.canvas)
        self.centerOnScreen()
        """
        ========================================================================================
        TEST
        ========================================================================================
        """
        self.canvas.signal_AISs_selected.connect(self.get_aiss)
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
        a_h_layout = QHBoxLayout()
        a_h_layout.addWidget(self._add_slider())
        # off
        button = QPushButton("TEST")
        button.clicked.connect(self.switch_manipulator)

        self.right_layout = QVBoxLayout()
        self.right_layout.addLayout(a_h_layout)
        self.right_layout.addWidget(button)

    # end def
    def _add_slider(self):
        ambient_lights = QGroupBox("滑条测试")
        ambient_lights_layout = QVBoxLayout(ambient_lights)

        button = QPushButton("ambient_light")
        # button.clicked.connect(partial(self.add_ambient_light, 1.0))

        # 创建 QLabel 用于显示滑条的值
        ambient_light_intensity_label = QLabel("值：1.0")

        def _slider_value_changed(label: QLabel, fun: Callable, value: int):
            # 当滑条值改变时调用的函数
            intensity = value / 100  # 数值转为浮点数
            label.setText(f"值：{intensity}")
            if callable(fun):
                fun(intensity)

        # end def
        # 创建滑条
        ambient_light_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        ambient_light_intensity_slider.setMinimum(1)
        ambient_light_intensity_slider.setMaximum(1000)
        ambient_light_intensity_slider.setValue(100)  # 设置初始值
        ambient_light_intensity_slider.valueChanged.connect(
            partial(_slider_value_changed, ambient_light_intensity_label, None)
        )
        # add
        ambient_lights_layout.addWidget(button)
        ambient_lights_layout.addWidget(ambient_light_intensity_label)
        ambient_lights_layout.addWidget(ambient_light_intensity_slider)

        return ambient_lights

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
    def switch_manipulator(self):
        if self.canvas.manipulator.HasActiveMode():
            self.canvas.manipulator.Detach()
        else:
            self.canvas.manipulator.Attach(self.selected_ais)
            self.canvas.manipulator.SetModeActivationOnDetection(True)
        self.canvas.update()

    # end def
    def get_aiss(self, signal: list):
        self.selected_ais = signal[0]

    # end def


# end class
def create_tetrahedron(edge_length):
    # 创建四个顶点
    v1 = BRepBuilderAPI_MakeVertex(gp_Pnt(0, 0, 0)).Vertex()
    v2 = BRepBuilderAPI_MakeVertex(gp_Pnt(edge_length, 0, 0)).Vertex()
    v3 = BRepBuilderAPI_MakeVertex(gp_Pnt(edge_length / 2, edge_length * 0.866, 0)).Vertex()
    v4 = BRepBuilderAPI_MakeVertex(
        gp_Pnt(edge_length / 2, edge_length * 0.288, edge_length * 0.816)
    ).Vertex()

    # 创建 6 条边
    edge1 = BRepBuilderAPI_MakeEdge(v1, v2).Edge()
    edge2 = BRepBuilderAPI_MakeEdge(v2, v3).Edge()
    edge3 = BRepBuilderAPI_MakeEdge(v3, v1).Edge()
    edge4 = BRepBuilderAPI_MakeEdge(v1, v4).Edge()
    edge5 = BRepBuilderAPI_MakeEdge(v2, v4).Edge()
    edge6 = BRepBuilderAPI_MakeEdge(v3, v4).Edge()

    # 创建四个线框
    wire1 = BRepBuilderAPI_MakeWire(edge1, edge5, edge4).Wire()
    wire2 = BRepBuilderAPI_MakeWire(edge1, edge2, edge3).Wire()
    wire3 = BRepBuilderAPI_MakeWire(edge2, edge6, edge5).Wire()
    wire4 = BRepBuilderAPI_MakeWire(edge3, edge4, edge6).Wire()

    # 创建四个面
    face1 = BRepBuilderAPI_MakeFace(wire1).Face()
    face2 = BRepBuilderAPI_MakeFace(wire2).Face()
    face3 = BRepBuilderAPI_MakeFace(wire3).Face()
    face4 = BRepBuilderAPI_MakeFace(wire4).Face()

    # 创建正四面体
    # tetrahedron = BRepBuilderAPI_MakeSolid(face1, face2, face3, face4).Solid()
    builder = BRep_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    builder.Add(shell, face1)
    builder.Add(shell, face2)
    builder.Add(shell, face3)
    builder.Add(shell, face4)

    return shell


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    tetrahedron = create_tetrahedron(1)
    ais_tetrahedron = AIS_Shape(tetrahedron)
    ais_tetrahedron.SetColor(COLOR(255, 255, 255)())
    gui.display(ais_tetrahedron, True)
    gui.canvas.attached_ais = ais_tetrahedron
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
