from context import *


def makeFace(left_top: gp_Pnt, right_bottom: gp_Pnt, *radius: float) -> TopoDS_Shape:
    # 左上角点
    p1 = left_top
    # 左下角点
    p2 = gp_Pnt(left_top.X(), right_bottom.Y(), left_top.Z())
    # 右下角点
    p3 = right_bottom
    # 右上角点
    p4 = gp_Pnt(right_bottom.X(), left_top.Y(), left_top.Z())

    # 创建边
    l1 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p1, p2).Value()).Edge()
    l2 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p2, p3).Value()).Edge()
    l3 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p3, p4).Value()).Edge()
    l4 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p4, p1).Value()).Edge()

    if not radius:
        # 创建线段
        wire = BRepBuilderAPI_MakeWire()
        wire.Add(l1)
        wire.Add(l2)
        wire.Add(l3)
        wire.Add(l4)

        # 创建面
        face = BRepBuilderAPI_MakeFace(wire.Wire())
        return face.Shape()

    # # Making the 2dFillet
    # f = ChFi2d_AnaFilletAlgo()
    # f.Init(l1, l2, gp_Pln())
    # f.Perform(*radius)
    # fillet2d_1 = f.Result(l1, l2)
    # # Making the 2dFillet
    # f.Init(l2, l3, gp_Pln())
    # f.Perform(*radius)
    # fillet2d_2 = f.Result(l2, l3)
    # # Making the 2dFillet
    # f.Init(l3, l4, gp_Pln())
    # f.Perform(*radius)
    # fillet2d_3 = f.Result(l3, l4)
    # # Making the 2dFillet
    # f.Init(l4, l1, gp_Pln())
    # f.Perform(*radius)
    # fillet2d_4 = f.Result(l4, l1)

    wire = BRepBuilderAPI_MakeWire()
    wire.Add(l1)
    # wire.Add(fillet2d_1)
    wire.Add(l2)
    # wire.Add(fillet2d_2)
    wire.Add(l3)
    # wire.Add(fillet2d_3)
    wire.Add(l4)
    # wire.Add(fillet2d_4)

    # 创建面
    face = BRepBuilderAPI_MakeFace(wire.Wire())

    filleter = BRepFilletAPI_MakeFillet2d(face.Face())
    explorer = BRepTools_WireExplorer(wire.Wire())
    while explorer.More():
        vertex = explorer.CurrentVertex()
        filleter.AddFillet(vertex, *radius)
        explorer.Next()
    filleter.Shape()

    a = filleter.Shape()
    print(a.ShapeType)
    b = topods.Face(a)
    return a


# end def


# end class
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    main_face = makeFace(gp_Pnt(0, 0, 0), gp_Pnt(5, 5, 0))
    add_piece = makeFace(gp_Pnt(5, 0, 0), gp_Pnt(15, 2, 0))
    added_face = BRepAlgoAPI_Fuse(main_face, add_piece).Shape()

    shapeUpgrade = ShapeUpgrade_UnifySameDomain(added_face, True, True, False)
    shapeUpgrade.Build()
    consolidatedShape = shapeUpgrade.Shape()

    cut_piece = makeFace(gp_Pnt(1, 0, 0), gp_Pnt(3, 2, 0), 0.1)

    cuttled_face = BRepAlgoAPI_Cut(consolidatedShape, cut_piece).Shape()

    # ais_face = AIS_Shape(cut_piece)
    # ais_face = AIS_Shape(added_face)
    ais_face = AIS_Shape(cuttled_face)
    gui.display(ais_face, True)
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
