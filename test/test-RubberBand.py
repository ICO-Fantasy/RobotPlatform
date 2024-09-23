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
        self.v3d = self.canvas.viewer3d
        self.setCentralWidget(self.canvas)
        self.centerOnScreen()

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
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    box_shape = BRepPrimAPI_MakeBox(10, 10, 10).Shape()
    ais_box = AIS_Shape(box_shape)
    a_trsf = gp_Trsf()
    a_trsf.SetTranslation(gp_Vec(3, 2, 6))
    ais_box.SetLocalTransformation(a_trsf)
    gui.display(ais_box, True)
    gui.v3d.FitAll()
    a_RubberBand = AIS_RubberBand()
    a_RubberBand.SetRectangle(400, 400, 600, 600)
    a_RubberBand.SetLineType(Aspect_TOL_SOLID)  # 设置边框线型为实线
    # a_RubberBand.SetFillColor(Quantity_NOC_BLUE2)  # 设置填充颜色为蓝色
    a_RubberBand.SetFillTransparency(0.8)  # 设置矩形填充的透明度为 0.8
    a_RubberBand.SetFillColor(COLOR.OCC_RED)  # 设置填充颜色为蓝色
    a_RubberBand.SetLineColor(COLOR.OCC_RED)  # 设置线颜色
    a_RubberBand.SetFilling(True)  # 设置填充
    gui.display(a_RubberBand, True)
    b_RubberBand = AIS_RubberBand()
    b_RubberBand.SetRectangle(200, 200, 400, 400)
    b_RubberBand.SetLineType(Aspect_TOL_DOT)  # 设置边框线型为虚线
    # b_RubberBand.SetFillColor(Quantity_NOC_GREEN2)  # 设置填充颜色为蓝色
    # b_RubberBand.SetFilling(False)  # 设置填充
    gui.display(b_RubberBand, True)


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
