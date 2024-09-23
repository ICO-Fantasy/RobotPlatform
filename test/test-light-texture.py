import os
import sys
from functools import partial

from context import *


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
        self.viewer = self.canvas.viewer3d.Viewer
        self.v3d = self.canvas.viewer3d
        # 光线追踪渲染
        # self.v3d.SetRaytracingMode(4)
        # 光栅化渲染
        self.v3d.SetRasterizationMode()
        # self.setCentralWidget(self.canvas)
        self.centerOnScreen()
        """
        ========================================================================================
        TEST
        ========================================================================================
        """
        self.render_mode_flag = True
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
        a_h_layout = QHBoxLayout()
        self.right_layout.addLayout(a_h_layout)
        direction_lights = self._direction_lights_layout()
        a_h_layout.addWidget(direction_lights)
        ambient_lights = self._ambient_lights_layout()
        a_h_layout.addWidget(ambient_lights)
        # off
        button = QPushButton("light_off")
        button.clicked.connect(self.turn_off_light)
        self.right_layout.addWidget(button)

    # end def
    def _direction_lights_layout(self):
        direction_lights = QGroupBox("平行光")
        direction_lights_layout = QVBoxLayout(direction_lights)
        button_dict = {
            "V3d_Xpos": partial(self.add_direction_light, 0),
            "V3d_Ypos": partial(self.add_direction_light, 1),
            "V3d_Zpos": partial(self.add_direction_light, 2),
            "V3d_Xneg": partial(self.add_direction_light, 3),
            "V3d_Yneg": partial(self.add_direction_light, 4),
            "V3d_Zneg": partial(self.add_direction_light, 5),
            "V3d_XposYpos": partial(self.add_direction_light, 6),
            "V3d_XposZpos": partial(self.add_direction_light, 7),
            "V3d_YposZpos": partial(self.add_direction_light, 8),
            "V3d_XnegYneg": partial(self.add_direction_light, 9),
            "V3d_XnegYpos": partial(self.add_direction_light, 10),
            "V3d_XnegZneg": partial(self.add_direction_light, 11),
            "V3d_XnegZpos": partial(self.add_direction_light, 12),
            "V3d_YnegZneg": partial(self.add_direction_light, 13),
            "V3d_YnegZpos": partial(self.add_direction_light, 14),
            "V3d_XposYneg": partial(self.add_direction_light, 15),
            "V3d_XposZneg": partial(self.add_direction_light, 16),
            "V3d_YposZneg": partial(self.add_direction_light, 17),
            "V3d_XposYposZpos": partial(self.add_direction_light, 18),
            "V3d_XposYnegZpos": partial(self.add_direction_light, 19),
            "V3d_XposYposZneg": partial(self.add_direction_light, 20),
            "V3d_XnegYposZpos": partial(self.add_direction_light, 21),
            "V3d_XposYnegZneg": partial(self.add_direction_light, 22),
            "V3d_XnegYposZneg": partial(self.add_direction_light, 23),
            "V3d_XnegYnegZpos": partial(self.add_direction_light, 24),
            "V3d_XnegYnegZneg": partial(self.add_direction_light, 25),
        }
        for button_name, button_method in button_dict.items():
            button = QPushButton(button_name)
            button.clicked.connect(button_method)
            direction_lights_layout.addWidget(button)
        return direction_lights

    # end def
    def _ambient_lights_layout(self):
        ambient_lights = QGroupBox("环境光")
        ambient_lights_layout = QVBoxLayout(ambient_lights)
        ambient_light_button = QPushButton("ambient_light")
        ambient_light_button.clicked.connect(partial(self.add_ambient_light, 1.0))
        # 输入框，输入光追的层数
        self.raytracing_depth_input = QLineEdit("3")
        set_raytracing_button = QPushButton("开启光追")
        set_raytracing_button.clicked.connect(partial(self.set_raytracing))
        rasterization_button = QPushButton("开启光栅")
        rasterization_button.clicked.connect(partial(self.set_rasterization))
        # 创建滑条
        self.ambient_light_intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.ambient_light_intensity_slider.setMinimum(1)
        self.ambient_light_intensity_slider.setMaximum(1000)
        self.ambient_light_intensity_slider.setValue(100)  # 设置初始值
        self.ambient_light_intensity_slider.valueChanged.connect(self._slider_value_changed)

        # 创建 QLabel 用于显示滑条的值
        self.ambient_light_intensity_label = QLabel("Slider Value: 1.0")

        ambient_lights_layout.addWidget(ambient_light_button)
        ambient_lights_layout.addWidget(self.ambient_light_intensity_label)
        ambient_lights_layout.addWidget(self.ambient_light_intensity_slider)
        ambient_lights_layout.addWidget(self.raytracing_depth_input)
        ambient_lights_layout.addWidget(set_raytracing_button)
        ambient_lights_layout.addWidget(rasterization_button)

        return ambient_lights

    # end def
    def _slider_value_changed(self, value):
        # 当滑条值改变时调用的函数
        intensity = value / 100  # 数值转为浮点数
        self.ambient_light_intensity_label.setText(f"光照强度：{intensity}")
        self.add_ambient_light(intensity)

    # end def
    def turn_off_light(self):
        while self._activated_light:
            self.viewer.SetLightOff(self._activated_light.pop())
        # end while
        if self.ambient_light:
            self.viewer.SetLightOff(self.ambient_light)
            self.ambient_light = None
        self.viewer.Update()

    # end def
    def add_direction_light(self, direction):
        # 添加平行光
        head_light = V3d_DirectionalLight()
        head_light.SetColor(COLOR(255, 255, 255)())
        head_light.SetDirection(direction)
        head_light.SetHeadlight(True)  # *设置灯光与相机保持一致

        self.viewer.AddLight(head_light)
        self.viewer.SetLightOn(head_light)
        self._activated_light.append(head_light)
        self.viewer.Update()

    # end def
    def add_ambient_light(self, intensity):
        # 添加环境光
        if not self.ambient_light:
            self.ambient_light = V3d_AmbientLight()
            self.ambient_light.SetColor(COLOR(255, 255, 255)())
            self.ambient_light.SetIntensity(intensity)
            # self.ambient_light.SetAttenuation()  # 衰减 (常数项，一次项)

            self.viewer.AddLight(self.ambient_light)
        else:
            self.viewer.SetLightOff(self.ambient_light)
            self.ambient_light.SetIntensity(intensity)

        self.viewer.SetLightOn(self.ambient_light)
        self.viewer.Update()

    # end def
    def set_raytracing(self):
        # 获取 self.raytracing_depth_input 中的值
        depth = int(self.raytracing_depth_input.text())
        self.canvas.viewer3d.SetRaytracingMode(depth)

    # end def
    def set_rasterization(self):
        self.canvas.viewer3d.SetRasterizationMode()

    # end def
    def add_position_light(self, direction):
        # 添加位置光
        position_light = V3d_PositionalLight()
        position_light.SetDirection(direction)
        self.viewer.AddLight(position_light)
        self.viewer.SetLightOn(position_light)
        self._activated_light.append(position_light)
        self.viewer.Update()

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
    gui.canvas.viewer3d.View.SetBgGradientColors(
        COLOR(125, 125, 125)(),
        COLOR(0, 0, 0)(),
        Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
        True,
    )
    # 开启灯光
    gui.viewer.SetLightOn()
    # make box
    box_shape2 = BRepPrimAPI_MakeBox(gp_Pnt(15, 15, 0), gp_Pnt(25, 25, 10)).Shape()
    # 创建金属材质
    iron_material = Graphic3d_MaterialAspect(
        Graphic3d_NameOfMaterial.Graphic3d_NameOfMaterial_Steel
    )
    # new_material.SetAlpha(0.5)
    # material.SetColor(getColor(0, 0, 0))

    copper_material = Graphic3d_MaterialAspect(
        Graphic3d_NameOfMaterial.Graphic3d_NameOfMaterial_Copper
    )

    iron_texture_file = r"iron_texture.bmp"
    # 创建 AIS_TexturedShape
    box_shape = read_step(r"D:\ICO\RobotPlatform\robot-mods\robot.STEP")
    # box_shape = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    texture_shape = AIS_TexturedShape(box_shape)
    texture_shape.SetTextureFileName(iron_texture_file)
    texture_shape.SetTextureMapOn()
    texture_shape.SetTextureScale(True, 1.0, 1.0)
    texture_shape.SetTextureRepeat(True, 1.0, 1.0)
    texture_shape.SetTextureOrigin(True, 0.0, 0.0)
    texture_shape.SetDisplayMode(AIS_DisplayMode.AIS_Shaded)
    new_prb = Graphic3d_PBRMaterial()
    new_prb.SetMetallic(0.0)
    new_prb.SetRoughness(0.2)
    new_prb.SetIOR(1)
    new_prb.SetColor(COLOR(216, 113, 50)())
    copper_material.SetPBRMaterial(new_prb)
    texture_shape.SetMaterial(copper_material)
    gui.display(texture_shape, True)

    texture_shape2 = AIS_TexturedShape(box_shape2)
    texture_shape2.SetTextureFileName(iron_texture_file)
    texture_shape2.SetTextureMapOn()
    texture_shape2.SetTextureScale(True, 1.0, 1.0)
    texture_shape2.SetTextureRepeat(True, 1.0, 1.0)
    texture_shape2.SetTextureOrigin(True, 0.0, 0.0)
    texture_shape2.SetDisplayMode(AIS_DisplayMode.AIS_Shaded)
    texture_shape2.SetMaterial(copper_material)
    gui.display(texture_shape2, True)
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
