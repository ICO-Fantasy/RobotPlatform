import itertools
import math
import sys
from typing import Callable

# pyOCC
from OCC.Core.AIS import AIS_InteractiveObject, AIS_Shape
from OCC.Core.Aspect import Aspect_GradientFillMethod
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
)
from OCC.Core.GCPnts import GCPnts_TangentialDeflection
from OCC.Core.Geom import Geom_TrimmedCurve
from OCC.Core.GeomAbs import GeomAbs_CurveType
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.Core.gp import gp_Dir, gp_EulerSequence, gp_Pln, gp_Pnt, gp_Quaternion, gp_Trsf, gp_Vec
from OCC.Core.TopAbs import TopAbs_ShapeEnum
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape

# PySide6
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow

# local
from pyOCC import getColor, read_step
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
    def display(self, input, update=True):
        if isinstance(input, [AIS_InteractiveObject, AIS_Shape]):
            self.canvas.viewer3d.Context.Display(input, update)
        if isinstance(input, TopoDS_Shape):
            self.canvas.viewer3d.Context.Display(AIS_Shape(input), update)

    # end def
    def centerOnScreen(self):
        # 获取屏幕的尺寸
        primary_screen = QGuiApplication.primaryScreen().size()
        size = self.geometry()
        x = primary_screen.width() - size.width()  #  2
        y = 0.7 * (primary_screen.height() - size.height())  #  2
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
    test_shape = read_step(r"./testSmall.STEP")
    reT = gp_Trsf()
    req = gp_Quaternion()
    req.SetEulerAngles(gp_EulerSequence.gp_Extrinsic_XYZ, math.radians(90), 0, 0)
    reT.SetRotationPart(req)
    test_shape.Move(TopLoc_Location(reT))

    PlaneNormal = gp_Dir(1.0, 0.0, 0.0)
    thePln = gp_Pln(gp_Pnt(-1, 0, 0), PlaneNormal)
    the_face = BRepBuilderAPI_MakeFace(thePln).Face()

    aSection = BRepAlgoAPI_Section(test_shape, the_face)
    aSection.Build()
    if aSection.IsDone():
        sec_shape: TopoDS_Shape = aSection.Shape()

    topo_list: list[TopoDS_Shape] = []
    # 遍历
    edge_Exp = TopExp_Explorer(sec_shape, TopAbs_ShapeEnum.TopAbs_EDGE)
    while edge_Exp.More():
        a_edge = edge_Exp.Current()
        edge_Exp.Next()

        bBAC = BRepAdaptor_Curve(a_edge)
        if bBAC.GetType() == GeomAbs_CurveType.GeomAbs_BSplineCurve:
            # print(aBAC.GetType())
            topo_list.append(a_edge)

    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    itertools.cycle([getColor(255, 0, 0)])
    for key, anBSLine in enumerate(topo_list):
        gui.display(AIS_Shape(anBSLine), False)
        aCurve, _, _ = BRep_Tool.Curve(anBSLine)
        bBAC = BRepAdaptor_Curve(anBSLine)
        p1 = bBAC.Value(bBAC.FirstParameter())
        p2 = bBAC.Value(bBAC.LastParameter())
        print(p1.Y(), p2.Y())

        bbb = anBSLine.Reversed()
        bBAC = BRepAdaptor_Curve(bbb)
        p1 = bBAC.Value(bBAC.FirstParameter())
        p2 = bBAC.Value(bBAC.LastParameter())
        print(p1.Y(), p2.Y())

        # ppc1 = GeomAPI_ProjectPointOnCurve(p1, aCurve)
        # pa1 = ppc1.LowerDistanceParameter()
        # ppc2 = GeomAPI_ProjectPointOnCurve(p2, aCurve)
        # pa2 = ppc2.LowerDistanceParameter()
        break
    # """
    # ========================================================================================
    # TEST
    # ========================================================================================
    # """
    # trim_param = 1
    # new_topo_list = []
    # for aBS in topo_list:
    #     aBAC = BRepAdaptor_Curve(aBS)
    #     p1 = aBAC.Value(aBAC.FirstParameter())
    #     p2 = aBAC.Value(aBAC.LastParameter())
    #     if p1.Y() > p2.Y():
    #         p1, p2 = p2, p1
    #     p1.SetY(p1.Y() + trim_param)
    #     p2.SetY(p2.Y() - trim_param)

    #     aCurve, _, _ = BRep_Tool.Curve(aBS)

    #     ppc1 = GeomAPI_ProjectPointOnCurve(p1, aCurve)
    #     pa1 = ppc1.LowerDistanceParameter()
    #     ppc2 = GeomAPI_ProjectPointOnCurve(p2, aCurve)
    #     pa2 = ppc2.LowerDistanceParameter()

    #     new_topo = BRepBuilderAPI_MakeEdge(aCurve, pa1, pa2).Edge()

    #     new_topo_list.append(new_topo)
    #     break

    # gui.display(test_shape, True)
    # gui.display(sec_shape, True)
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
