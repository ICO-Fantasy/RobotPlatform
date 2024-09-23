import os
import sys

from context import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)
        self.canvas = qtViewer3dWidget(self)
        self.set_background_color(
            (37, 55, 113),
            (36, 151, 132),
            Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
        )
        self.setCentralWidget(self.canvas)
        self.centerOnScreen()
        # 去掉窗口标题
        # self.setWindowFlags(Qt.FramelessWindowHint)

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
    def set_background_color(self, color1=None, color2=None, fill_method=None):
        """ """
        if color1 and color2 and fill_method:
            pass
        else:
            color1, color2, fill_method = self._bg_gradient_color
        self.canvas.viewer3d.View.SetBgGradientColors(
            getColor(color1), getColor(color2), fill_method, True
        )


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
def test():
    app = QApplication().instance()
    if not app:
        app = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    gui.canvas.InitDriver()
    gui.canvas.qApp = app

    # region test

    origin = gp_Pnt(5.0, 5.0, 0.0)
    # N 是主方向（Z 轴），Vx 是 X 轴方向
    origin_ax2 = gp_Ax2(origin, gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    radius = 5.0
    hight = 10.0
    cylinder = BRepPrimAPI_MakeCylinder(origin_ax2, radius, hight).Shape()
    ais_cylinder = AIS_Shape(cylinder)
    ais_cylinder.SetColor(getColor(0, 255, 0))
    ais_cylinder.SetTransparency()
    gui.canvas.viewer3d.Context.Display(ais_cylinder, True)

    # endregion

    gui.canvas.viewer3d.FitAll()
    """test"""
    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    test()
# end main
