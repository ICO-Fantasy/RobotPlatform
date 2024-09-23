import math

from context import *


# end class
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    a_pln = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    a_face = BRepBuilderAPI_MakeFace(a_pln, 0, 10, 0, 10).Shape()
    ais_face = AIS_Shape(a_face)
    # a_trsf = gp_Trsf()
    # a_trsf.SetTranslation(gp_Vec(3, 2, 6))
    # ais_face.SetLocalTransformation(a_trsf)
    gui.display(ais_face, True)

    a_pln = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    a_face = BRepBuilderAPI_MakeFace(a_pln, 0, 10, 0, 10).Shape()
    ais_face = AIS_Shape(a_face)
    a_trsf = gp_Trsf()
    a_trsf.SetRotation(gp_Ax1(), math.radians(45))
    ais_face.SetLocalTransformation(a_trsf)
    ais_face.SetColor(getColor(255, 0, 0))
    gui.display(ais_face, True)

    gui.canvas.display_graduated_trihedron()
    gui.canvas.display_origin_trihedron()
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
