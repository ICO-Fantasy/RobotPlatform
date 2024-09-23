from pprint import pprint

from context import *


class Edge:
    def __init__(self, edge: TopoDS_Edge):
        self.topo_edge: TopoDS_Edge = edge
        self._get_ends()

    # end alternate constructor
    def _get_ends(self):
        aBAC = BRepAdaptor_Curve(self.topo_edge)
        self.start = aBAC.Value(aBAC.FirstParameter())
        self.end = aBAC.Value(aBAC.LastParameter())
        if self.start.Y() > self.end.Y():
            self.start, self.end = self.end, self.start

    # end def
    def __repr__(self) -> str:
        return f"{self.start.Y()}->{self.end.Y()}"

    # end def


# end def
def getEdges(shape: TopoDS_Shape):
    result: list[Edge] = []
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while explorer.More():
        e = explorer.Current()
        edge = Edge(topods.Edge(e))
        result.append(edge)
        explorer.Next()
    # end while
    return result


# end def
def make_piece(edge: Edge):
    p1 = edge.start
    p2 = edge.end
    p3 = gp_Pnt(p2.X(), p2.Y(), 0)
    p4 = gp_Pnt(p1.X(), p1.Y(), 0)
    l1 = edge.topo_edge
    l2 = BRepBuilderAPI_MakeEdge(p2, p3).Edge()
    l3 = BRepBuilderAPI_MakeEdge(p3, p4).Edge()
    l4 = BRepBuilderAPI_MakeEdge(p4, p1).Edge()
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(l1)
    wire_maker.Add(l2)
    wire_maker.Add(l3)
    wire_maker.Add(l4)
    face_maker = BRepBuilderAPI_MakeFace(wire_maker.Wire(), True)
    return face_maker.Face()


# end def
def add_edge(edge_dict: dict, edge_list: list[Edge]):
    # test = []
    for e in edge_list:
        if e.start.IsEqual(edge_dict["end"], 0.001):
            edge_dict["end"] = e.end
            edge_dict["edge"].append(e)
            return False
        elif e.end.IsEqual(edge_dict["start"], 0.001):
            edge_dict["start"] = e.start
            edge_dict["edge"].insert(0, e)
            return False
    #     test.append(
    #         f"start {edge_dict['start'].X():1f}, end {edge_dict['end'].X():1f}, ps {e.start.X():1f}, pe {e.end.X():1f}"
    #     )
    # pprint(test)
    return True


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    box_shape = read_step(r".\test4Small.STEP")

    ais_box_shape = AIS_Shape(box_shape)
    ais_box_shape.SetTransparency(0.5)
    ais_box_shape.SetColor(getColor(125, 125, 125))
    # gui.display(ais_box_shape, False)

    cross_plane = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(-950.0, 0, 0), gp_Dir(1, 0, 0))).Face()
    # cross_plane = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(-972.8, 0, 0), gp_Dir(1, 0, 0))).Face()
    cross_shape = BRepAlgoAPI_Section(box_shape, cross_plane).Shape()

    # ais_box = AIS_Shape(cross_shape)
    # gui.display(ais_box, False)

    # gui.v3d.FitAll()
    # return None

    edges: list[Edge] = getEdges(cross_shape)
    # 移除竖直的线
    new_edge: list[Edge] = []
    z_dir = gp_Vec(0, 0, 1)
    for e in edges:
        if gp_Vec(e.start, e.end).IsParallel(z_dir, 0.1):
            continue
        else:
            new_edge.append(e)
    # end for
    new_edge = sorted(new_edge, key=lambda x: x.start.Y())
    first_dict = {
        "start": gp_Pnt(),
        "end": gp_Pnt(),
        "edge": [],
    }
    second_list = []
    # for i in new_edge:
    #     print(printPnt(i.start, 1, True) + "  " + printPnt(i.end, 1, True))
    finish = False
    while not finish:
        if not first_dict["edge"]:
            first_dict["start"] = e.start
            first_dict["end"] = e.end
            first_dict["edge"].append(e)
        # end for
        finish = add_edge(first_dict, new_edge)

    # end for
    for e in new_edge:
        if e not in first_dict["edge"]:
            second_list.append(e)
        # end if
    # end for

    for e in first_dict["edge"]:
        ais_piece = AIS_Shape(make_piece(e))
        ais_piece.SetColor(getColor(255, 0, 0))
        ais_piece.SetTransparency(0.5)
        gui.display(ais_piece, False)

    # for e in second_list:
    #     gui.display(AIS_Shape(make_piece(e)), False)
    # end for

    for e in edges:
        ais_edges = AIS_Shape(e.topo_edge)
        # ais_edges.SetColor(getColor(255, 0, 0))
        # ais_edges.SetTransparency(0.5)
        gui.display(ais_edges, False)
    # end for

    gui.view.Update()
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
