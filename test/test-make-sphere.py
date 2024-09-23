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

    sphere = BRepPrimAPI_MakeSphere(origin, 5.0).Shape()
    ais_sphere = AIS_Shape(sphere)
    ais_sphere.SetColor(COLOR.OCC_BLUE)
    ais_sphere.SetTransparency()
    gui.canvas.viewer3d.Context.Display(ais_sphere, True)

    # endregion

    gui.canvas.viewer3d.FitAll()
    """test"""
    # 窗口置顶
    gui.raise_()
    app.exec()


if __name__ == "__main__":
    test()
# end main
