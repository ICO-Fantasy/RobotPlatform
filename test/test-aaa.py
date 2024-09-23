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
def make_box():
    box_shape = BRepPrimAPI_MakeBox(5, 5, 5).Shape()
    # box_shape = BRepPrimAPI_MakeBox(
    #     random.randint(0, 10), random.randint(0, 100), random.randint(0, 100)
    # ).Shape()
    ais_box = AIS_Shape(box_shape)
    a_trsf = gp_Trsf()
    a_trsf.SetTranslation(
        gp_Vec(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    )
    ais_box.SetLocalTransformation(a_trsf)
    return ais_box


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    ais_list = [make_box() for i in range(5)]
    b = [gui.display(ais_box, True) for ais_box in ais_list]
    # c=[if ais_box not 1231 else gui.context.Erase(ais_box, True) for ais_box in ais_list)]
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
