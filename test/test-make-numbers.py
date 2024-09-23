import os
import sys
from typing import Callable

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
def make_number(number_string: str, location: gp_Pnt, direction: gp_Dir, size: float = 60.0):
    """根据输入的字符串构建数字浮雕

    Parameters
    ----------
    number_string : `str`, _description_
    location : `gp_Pnt`, _description_
    direction : `gp_Dir`, _description_
    size : `float`, 默认值 60 &emsp; 形状默认宽 30, 高 60

    Returns
    -------
    _description_ : `_type_`
    """

    number_dict: dict[int, list[tuple[float, float]]] = {
        0: [
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 29.0),
            (20.0, 29.0),
            (20.0, 10.0),
            (10.0, 10.0),
            (10.0, 50.0),
            (20.0, 50.0),
            (20.0, 31.0),
            (30.0, 31.0),
            (30.0, 60.0),
            (0.0, 60.0),
        ],
        1: [
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 50.0),
            (0.0, 50.0),
            (0.0, 60.0),
            (20.0, 60.0),
            (20.0, 10.0),
            (30.0, 10.0),
            (30.0, 0.0),
        ],
        2: [
            (0.0, 0.0),
            (0.0, 10.0),
            (18.94, 50.0),
            (10.0, 50.0),
            (10.0, 43.0),
            (0.0, 43.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 50.0),
            (11.06, 10.0),
            (30.0, 10.0),
            (30.0, 0.0),
        ],
        3: [
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
            (0.0, 50.0),
            (20.0, 50.0),
            (20.0, 35.0),
            (8.0, 35.0),
            (8.0, 25.0),
            (20.0, 25.0),
            (20.0, 10.0),
            (0.0, 10.0),
        ],
        4: [
            (15.0, 0.0),
            (15.0, 10.0),
            (0.0, 10.0),
            (0.0, 20.0),
            (5.0, 60.0),
            (15.0, 60.0),
            (10.0, 20.0),
            (15.0, 20.0),
            (15.0, 30.0),
            (25.0, 30.0),
            (25.0, 20.0),
            (30.0, 20.0),
            (30.0, 10.0),
            (25.0, 10.0),
            (25.0, 0.0),
        ],
        5: [
            (0.0, 0.0),
            (0.0, 10.0),
            (20.0, 10.0),
            (20.0, 25.0),
            (0.0, 25.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 50.0),
            (10.0, 50.0),
            (10.0, 35.0),
            (30.0, 35.0),
            (30.0, 0.0),
        ],
        6: [
            (0.0, 0.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 50.0),
            (10.0, 50.0),
            (10.0, 10.0),
            (20.0, 10.0),
            (20.0, 20.0),
            (12.0, 20.0),
            (12.0, 30.0),
            (30.0, 30.0),
            (30.0, 0.0),
        ],
        7: [
            (0.0, 0.0),
            (20.0, 50.0),
            (10.0, 50.0),
            (10.0, 40.0),
            (0.0, 40.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 50.0),
            (10.0, 0.0),
        ],
        8: [
            (0.0, 0.0),
            (0.0, 35.0),
            (20.0, 35.0),
            (20.0, 50.0),
            (10.0, 50.0),
            (10.0, 38.0),
            (0.0, 38.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 25.0),
            (10.0, 25.0),
            (10.0, 10.0),
            (20.0, 10.0),
            (20.0, 22.0),
            (30.0, 22.0),
            (30.0, 0.0),
        ],
        9: [
            (20.0, 0.0),
            (20.0, 50.0),
            (10.0, 50.0),
            (10.0, 40.0),
            (18.0, 40.0),
            (18.0, 30.0),
            (0.0, 30.0),
            (0.0, 60.0),
            (30.0, 60.0),
            (30.0, 0.0),
        ],
        10: [
            (0.0, 0.0),
            (10.0, 0.0),
            (15.0, 25.0),
            (20.0, 0.0),
            (30.0, 0.0),
            (24.0, 30.0),
            (30.0, 60.0),
            (20.0, 60.0),
            (15.0, 35.0),
            (10.0, 60.0),
            (0.0, 60.0),
            (6.0, 30.0),
        ],
        11: [
            (10.0, 0.0),
            (20.0, 0.0),
            (20.0, 30.0),
            (30.0, 60.0),
            (20.0, 60.0),
            (15.0, 45.0),
            (10.0, 60.0),
            (0.0, 60.0),
            (10.0, 30.0),
        ],
        12: [
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 10.0),
            (20.0, 10.0),
            (20.0, 50.0),
            (30.0, 50.0),
            (30.0, 60.0),
            (0.0, 60.0),
            (0.0, 50.0),
            (10.0, 50.0),
            (10.0, 10.0),
            (0.0, 10.0),
        ],
        44: [
            (10.0, 10.0),
            (68.0, 10.0),
            (68.0, 0.0),
            (78.0, 15.0),
            (68.0, 30.0),
            (68.0, 20.0),
            (57.0, 20.0),
            (47.0, 50.0),
            (57.0, 80.0),
            (47.0, 80.0),
            (42.0, 65.0),
            (37.0, 80.0),
            (27.0, 80.0),
            (37.0, 50.0),
            (27.0, 20.0),
            (20.0, 20.0),
            (20.0, 91.0),
            (50.0, 91.0),
            (80.0, 81.0),
            (80.0, 91.0),
            (65.0, 96.0),
            (80.0, 101.0),
            (80.0, 111.0),
            (50.0, 101.0),
            (20.0, 101.0),
            (20.0, 110.0),
            (30.0, 110.0),
            (15.0, 120.0),
            (0.0, 110.0),
            (10.0, 110.0),
        ],
    }

    number_list = []
    for i in number_string:
        try:
            index = int(i)
        except:
            if i.upper() == "X":
                index = 10
            elif i.upper() == "Y":
                index = 11
            elif i.upper() == "A":
                index = 44
            else:
                index = 12
        number_list.append(index)
    # end for

    scale_ratio = size / 60.0
    offset = (10.0 + 30.0) * scale_ratio

    final_face = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(final_face)

    # region 构造基础形状
    for num, index in enumerate(number_list):
        number_points = number_dict[index]
        wire_maker = BRepBuilderAPI_MakeWire()
        last_xz = None
        for p in number_points:
            if not last_xz:
                last_xz = (p[0] + num * offset, 0.0, p[1])
                continue
            # printPnt(gp_Pnt(*last_value))
            xz = (p[0] + num * offset, 0.0, p[1])
            wire_maker.Add(
                BRepBuilderAPI_MakeEdge(
                    gp_Pnt(*[i * scale_ratio for i in last_xz]),
                    gp_Pnt(*[i * scale_ratio for i in xz]),
                ).Edge()
            )
            last_xz = xz
        # end for
        end_value = (number_points[0][0] + num * offset, 0.0, number_points[0][1])
        wire_maker.Add(
            BRepBuilderAPI_MakeEdge(
                gp_Pnt(*[i * scale_ratio for i in last_xz]),
                gp_Pnt(*[i * scale_ratio for i in end_value]),
            ).Edge()
        )
        the_face = BRepBuilderAPI_MakeFace(wire_maker.Wire()).Face()
        builder.Add(final_face, the_face)

        # endregion
    # end for

    # region 缩放、旋转、平移形状到指定位置

    scale = gp_Trsf()
    scale.SetScaleFactor(scale_ratio)

    rot = gp_Trsf()
    quat = gp_Quaternion(
        gp_Vec(0.0, 0.0, 1.0),
        gp_Vec(direction.XYZ()).Angle(gp_Vec(1.0, 0.0, 0.0)),
        # gp_Vec(direction.XYZ()).AngleWithRef(gp_Vec(1.0, 0.0, 0.0), gp_Vec(0.0, 0.0, -1.0)),
    )
    rot.SetRotation(quat)

    trans = gp_Trsf()
    trans.SetTranslation(gp_Pnt(), location)

    transformed_face = BRepBuilderAPI_Transform(
        final_face, scale.Multiplied(trans.Multiplied(rot))
    ).Shape()

    # endregion

    return transformed_face


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    gui.canvas.display_graduated_trihedron()
    ld_list = [
        (gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)),
        # (gp_Pnt(70.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)),
        # (gp_Pnt(10.0, 10.0, 10.0), gp_Dir(1.0, 1.0, 0.0)),
        # (gp_Pnt(10.0, 10.0, 10.0), gp_Dir(0.0, 1.0, 0.0)),
        # (gp_Pnt(0.0, 0.0, 0.0), gp_Dir(-1.0, 1.0, 0.0)),
        # (gp_Pnt(0.0, 0.0, 0.0), gp_Dir(-1.0, 0.0, 0.0)),
        # (gp_Pnt(10.0, 10.0, 10.0), gp_Dir(-1.0, -1.0, 0.0)),
        # (gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, -1.0, 0.0)),
        # (gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, -1.0, 0.0)),
    ]

    number_string = "XY0123456789A"
    for l, d in ld_list:
        shape = make_number(number_string, l, d, 60.0)
        ais = AIS_Shape(shape)
        gui.display(ais, False)

    # gui.v3d.View_Front()
    gui.context.UpdateCurrentViewer()
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
