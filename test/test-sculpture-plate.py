import sys
from typing import Callable

# pyOCC
from OCC.Core.Addons import Font_FontAspect_Italic, Font_FontAspect_Regular, text_to_brep
from OCC.Core.AIS import AIS_InteractiveObject, AIS_Shape
from OCC.Core.Aspect import Aspect_GradientFillMethod
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.TopLoc import TopLoc_Location

# PySide6
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow

# local
from qtViewer3d import qtViewer3dWidget

Dislpay = Callable[[AIS_InteractiveObject, bool], None]


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
    txt_Str = "AB"
    width = 7.2
    length = 10
    thickness = 1
    txt_Font = "SimSun"
    txt_Size = 10  # 字体大小 (两个字节的宽度)

    box_shape = BRepPrimAPI_MakeBox(length, width, thickness).Shape()

    aFontAspect = Font_FontAspect_Regular
    font_shape = text_to_brep(txt_Str, txt_Font, aFontAspect, txt_Size, True)  # 从文字生成 Face
    aPrismVec = gp_Vec(0, 0, thickness)  # Vec face，进行 prism
    font_shape = BRepPrimAPI_MakePrism(font_shape, aPrismVec).Shape()  # 形成字符模板 TopoDS_Shape
    the_trsf = gp_Trsf()
    the_trsf.SetTranslation(gp_Vec(0, 0, 0))
    font_shape.Location(TopLoc_Location(the_trsf))

    cutter = BRepAlgoAPI_Cut(box_shape, font_shape)
    if cutter.IsDone():
        plate_shape = cutter.Shape()
    ais_box = AIS_Shape(plate_shape)
    gui.display(ais_box, True)
    gui.v3d.FitAll()
    return plate_shape


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
