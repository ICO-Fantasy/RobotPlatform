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
    # 创建一个 AIS_TextLabel 对象
    text_label = AIS_TextLabel()
    text_label.SetText("text")
    # 设置字体
    text_label.SetFont("SimSun")
    # 字体高度
    text_label.SetHeight(100.0)
    # 字体颜色
    text_label.SetColor(COLOR(0, 0, 0)())
    gui.display(text_label, True)

    persistence_text = AIS_TextLabel()
    persistence_text.SetText("text")
    # 设置字体
    persistence_text.SetFont("SimSun")
    # 字体高度
    persistence_text.SetHeight(100.0)
    # 字体颜色
    persistence_text.SetColor(COLOR(0, 0, 0)())
    # 设置持久化
    persistence_text.SetTransformPersistence(
        Graphic3d_TransformPers(
            Graphic3d_TransModeFlags.Graphic3d_TMF_2d,
            Aspect_TOTP_RIGHT_LOWER,
            Graphic3d_Vec2i(100, 200),
        )
    )
    gui.display(persistence_text, True)

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
