from context import *


# end class
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    wire_points = [
        (0.0, 0.0, 0.0),
        (5.0, 0.0, 0.0),
        (5.0, 5.0, 0.0),
        (7.0, 5.0, 0.0),
        (7.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.0),
    ]
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(
        BRepBuilderAPI_MakeEdge(gp_Pnt(*wire_points[-1]), gp_Pnt(*wire_points[0])).Edge()
    )
    last_p = None
    for p in wire_points:
        if not last_p:
            last_p = p
            continue
        edge = BRepBuilderAPI_MakeEdge(gp_Pnt(*last_p), gp_Pnt(*p))
        # ais_edge = AIS_Shape(edge.Edge())
        # ais_edge.SetColor(next(color_list_cycle))
        # gui.display(ais_edge, False)
        wire_maker.Add(edge.Edge())
        last_p = p
    # end for
    face = BRepBuilderAPI_MakeFace(wire_maker.Shape()).Face()

    # ais_face = AIS_Shape(face)
    # gui.display(ais_face, False)

    fillet = BRepFilletAPI_MakeFillet2d(face)
    #! 只能用 BRepTools_WireExplorer 来遍历，用 TopExp_Explorer 会报错
    explorer = BRepTools_WireExplorer(wire_maker.Wire())
    while explorer.More():
        vertex = explorer.CurrentVertex()
        fillet.AddFillet(vertex, 0.5)
        explorer.Next()
    fillet.Build()
    if fillet.IsDone():
        chamfered_face = fillet.Shape()
        ais_chamfered_face = AIS_Shape(chamfered_face)
        ais_chamfered_face.SetColor(COLOR.RED)
        # ais_chamfered_face.SetTransparency(0.5)
        gui.display(ais_chamfered_face, False)
    # end if

    # region 切割后的面

    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(0, 4, 0), gp_Pnt(2, 4, 0)).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(2, 4, 0), gp_Pnt(1, 5, 0)).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(1, 5, 0), gp_Pnt(2, 6, 0)).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(2, 6, 0), gp_Pnt(0, 6, 0)).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(0, 6, 0), gp_Pnt(0, 4, 0)).Edge())
    cut_face = BRepBuilderAPI_MakeFace(wire_maker.Wire()).Face()
    cutted_face = BRepAlgoAPI_Cut(face, cut_face).Shape()
    # ais_cutted_face = AIS_Shape(cutted_face)
    # ais_cutted_face.SetColor(COLOR.BLUE)
    # ais_cutted_face.SetTransparency(0.5)
    # gui.display(ais_cutted_face, False)

    # * 缝合组合体为单个面
    sewer = BRepBuilderAPI_Sewing()
    sewer.Init()
    sewer.Load(cutted_face)
    sewer.Perform()

    # * 从 Face 中构造 Wire
    fillet = BRepFilletAPI_MakeFillet2d(sewer.SewedShape())
    wire_maker = BRepBuilderAPI_MakeWire()
    explorer = TopExp_Explorer(cutted_face, TopAbs_EDGE)
    while explorer.More():
        edge = explorer.Current()
        wire_maker.Add(edge)
        explorer.Next()
    # end while

    # * 倒圆角
    #! 只能用 BRepTools_WireExplorer 来遍历，用 TopExp_Explorer 会报错
    explorer = BRepTools_WireExplorer(wire_maker.Wire())
    while explorer.More():
        vertex = explorer.CurrentVertex()
        fillet.AddFillet(vertex, 0.5)
        explorer.Next()
    fillet.Build()
    if fillet.IsDone():
        chamfered_face = fillet.Shape()
        up = gp_Trsf()
        up.SetTranslation(gp_Vec(0, 0, 1))
        ais_chamfered_face = AIS_Shape(chamfered_face.Moved(TopLoc_Location(up)))
        ais_chamfered_face.SetColor(COLOR.BLUE)
        ais_chamfered_face.SetTransparency(0.5)
        gui.display(ais_chamfered_face, False)
    # end if

    # endregion

    gui.canvas.display_graduated_trihedron()
    # gui.canvas.display_origin_trihedron(1)
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
