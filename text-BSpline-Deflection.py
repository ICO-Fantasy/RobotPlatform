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
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex
from OCC.Core.GCPnts import GCPnts_TangentialDeflection
from OCC.Core.Geom import Geom_TrimmedCurve
from OCC.Core.GeomAbs import GeomAbs_CurveType
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.gp import gp_Dir, gp_EulerSequence, gp_Pln, gp_Pnt, gp_Quaternion, gp_Trsf
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

    todo_list: list[TopoDS_Shape] = []
    # 遍历
    edge_Exp = TopExp_Explorer(sec_shape, TopAbs_ShapeEnum.TopAbs_EDGE)
    while edge_Exp.More():
        a_edge = edge_Exp.Current()
        edge_Exp.Next()

        aBAC = BRepAdaptor_Curve(a_edge)
        if aBAC.GetType() == GeomAbs_CurveType.GeomAbs_BSplineCurve:
            # print(aBAC.GetType())
            todo_list.append(a_edge)
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    itertools.cycle([getColor(255, 0, 0)])
    points: list[gp_Pnt] = []
    for key, e in enumerate(todo_list):
        anADeflect = 0.25 * 3.1415
        # 角度偏差 Angular deflection
        aCDeflect = 1e-1
        # 曲率偏差 Curvature deflection
        # 得到 Geom_Curve
        # aBAC=BRepAdaptor_Curve (theBSpline)
        aCurve, _, _ = BRep_Tool.Curve(e)
        # 离散为点
        aPointsOnCurve = GCPnts_TangentialDeflection()  #  切矢量偏离算法
        aCurveAdaptor = GeomAdaptor_Curve(aCurve)
        aPointsOnCurve.Initialize(aCurveAdaptor, anADeflect, aCDeflect)
        # if aPointsOnCurve.NbPoints() <= 2:
        #     continue
        print(f"{key}, 点的个数:{aPointsOnCurve.NbPoints()}")
        gui.display(AIS_Shape(e), False)
        i = 1
        while i <= aPointsOnCurve.NbPoints():
            # firstP = aPointsOnCurve.Parameter(i)
            # lastP = aPointsOnCurve.Parameter(i + 1)
            # tricurve = Geom_TrimmedCurve(aCurve, firstP, lastP)

            aU = aPointsOnCurve.Parameter(i)
            aPnt = aPointsOnCurve.Value(i)
            points.append(aPnt)
            i += 1
    for p in points:
        the_p = BRepBuilderAPI_MakeVertex(p).Shape()
        gui.display(AIS_Shape(the_p), True)
    # for topo in todo_list:
    #     gui.display(AIS_Shape(topo), True)

    ais_test = AIS_Shape(test_shape)
    gui.display(ais_test, True)
    ais_sec = AIS_Shape(sec_shape)
    gui.display(ais_sec, True)
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
