import math
import time

from context import *

LINEAR_TOLERANCE_LIST = [
    1e-6,
    1e-4,
    1e-2,
    0.1,
]
LINEAR_TOLERANCE = 0.1


class Edge:
    def __init__(self, edge: TopoDS_Edge):
        self.topo_edge: TopoDS_Edge = edge
        self._get_ends()

    # end alternate constructor
    def _get_ends(self):
        aBAC = BRepAdaptor_Curve(self.topo_edge)
        self.start = aBAC.Value(aBAC.FirstParameter())
        self.end = aBAC.Value(aBAC.LastParameter())
        if self.start.Distance(gp_Pnt()) > self.end.Distance(gp_Pnt()):
            self.start, self.end = self.end, self.start

    # end def
    def __repr__(self) -> str:
        return f"{print_gp_Pnt(self.start,1,True,False)}->{print_gp_Pnt(self.end,1,True,False)}"

    # end def
    @property
    def start_2d(self):
        return gp_Pnt2d(self.start.X(), self.start.Y())

    # end def
    @property
    def end_2d(self):
        return gp_Pnt2d(self.end.X(), self.end.Y())

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
    global GUI
    for e in edge_list:
        if e.start.Distance(edge_dict["end"]) < LINEAR_TOLERANCE:
            d = e.start_2d.Distance(edge_dict["origin"])
            # print(f"start distance: {d}")
            if e.start_2d.Distance(edge_dict["origin"]) > edge_dict[
                "start_distance"
            ] and e.start_2d.Distance(edge_dict["origin"]) < e.end_2d.Distance(edge_dict["origin"]):
                edge_dict["end"] = e.end
                edge_dict["start_distance"] = e.start_2d.Distance(edge_dict["origin"])
                edge_dict["edge"].append(e)

                ais_piece = AIS_Shape(e.topo_edge)
                ais_piece.SetWidth(5)
                ais_piece.SetColor(getColor(255, 0, 0))
                # GUI.display(ais_piece, True)
                # time.sleep(0.2)
                GUI.v3d.FitAll()
                return False
        ed = e.end.Distance(edge_dict["start"])
        if e.end.Distance(edge_dict["start"]) < LINEAR_TOLERANCE:
            d = e.end_2d.Distance(edge_dict["origin"])
            print(f"end distance: {d}")
            if e.end_2d.Distance(edge_dict["origin"]) > edge_dict[
                "end_distance"
            ] and e.start_2d.Distance(edge_dict["origin"]) > e.end_2d.Distance(edge_dict["origin"]):
                edge_dict["start"] = e.start
                edge_dict["end_distance"] = e.end_2d.Distance(edge_dict["origin"])
                edge_dict["edge"].insert(0, e)

                ais_piece = AIS_Shape(e.topo_edge)
                ais_piece.SetWidth(5)
                ais_piece.SetColor(getColor(0, 255, 0))
                # GUI.display(ais_piece, True)
                # time.sleep(0.2)
                GUI.v3d.FitAll()
                return False
    return True


# end def


def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    gui.canvas.display_graduated_trihedron()
    gui.canvas.viewer3d.View_Right()

    input_point = gp_Pnt(1000, 0, 0)
    input_dir = gp_Dir(1, 0, 0)

    #! 读取工件
    box_shape = read_step(r".\laser-test1-Small-01.stp")
    ais_box_shape = AIS_Shape(box_shape)
    ais_box_shape.SetTransparency(0.9)
    ais_box_shape.SetColor(getColor(125, 125, 125))
    gui.display(ais_box_shape, False)

    #! 创建截面并切割
    cross_plane = BRepBuilderAPI_MakeFace(gp_Pln(input_point, input_dir)).Face()
    cross_shape = BRepAlgoAPI_Section(box_shape, cross_plane).Shape()

    # ais_cross = AIS_Shape(cross_shape)
    # gui.display(ais_cross, True)

    #! 获取截面线
    edges: list[Edge] = getEdges(cross_shape)

    # # * 移除竖直的线
    # new_edge: list[Edge] = []
    # z_dir = gp_Vec(0, 0, 1)
    # for e in edges:
    #     if gp_Vec(e.start, e.end).IsParallel(z_dir, 0.1):
    #         continue
    #     else:
    #         new_edge.append(e)
    # # end for

    #! 线排序，并获得按顺序的起点
    wire_maker = BRepBuilderAPI_MakeWire()
    container = TopTools_ListOfShape()
    for e in edges:
        container.Append(e.topo_edge)
    # end for
    wire_maker.Add(container)
    wire_explorer = BRepTools_WireExplorer(wire_maker.Wire())
    ordered_edges: list[Edge] = []
    while wire_explorer.More():
        a_edge = Edge(wire_explorer.Current())
        current_point = BRep_Tool.Pnt(wire_explorer.CurrentVertex())
        if a_edge.start.Distance(current_point) > a_edge.end.Distance(current_point):
            a_edge.start, a_edge.end = a_edge.end, a_edge.start

        ordered_edges.append(a_edge)
        wire_explorer.Next()
    # end while

    # region #! debug display

    for e in ordered_edges:
        color = next(color_list)
        ais_edge = AIS_Shape(e.topo_edge)
        ais_edge.SetColor(color)
        ais_edge.SetWidth(2)
        gui.display(ais_edge, False)

        start_vertex = BRepBuilderAPI_MakeVertex(e.start).Shape()
        ais_start = AIS_Shape(start_vertex)
        ais_start.SetColor(color)
        ais_start.SetWidth(5)
        gui.display(ais_start, True)
    # end for

    # endregion

    first_dict = {
        "start": gp_Pnt(),
        "start_distance": 0.0,
        "end": gp_Pnt(),
        "end_distance": 0.0,
        "edge": [],
        "origin": gp_Pnt2d(),
    }

    #! 找到其中一条边
    finish = False
    while not finish:
        if not first_dict["edge"]:
            first_dict["start"] = ordered_edges[0].start
            first_dict["end"] = ordered_edges[0].end
            first_dict["origin"] = ordered_edges[0].start_2d
            first_dict["edge"].append(ordered_edges[0])

            ais_vertex = AIS_Shape(BRepPrimAPI_MakeSphere(ordered_edges[0].start, 2).Shape())
            ais_vertex.SetColor(COLOR.RED)
            ais_vertex.SetTransparency(0.5)
            gui.display(ais_vertex, True)

        # end for
        finish = add_edge(first_dict, ordered_edges)

    # end for

    #! 划分另一条边
    second_list: list[Edge] = []
    for e in ordered_edges:
        if e not in first_dict["edge"]:
            second_list.append(e)
        # end if
    # end for

    # * 显示
    for e in first_dict["edge"]:
        ais_edge = AIS_Shape(e.topo_edge)
        ais_edge.SetColor(getColor(255, 0, 0))
        ais_edge.SetWidth(5)
        # print(
        #     "start: "
        #     + print_gp_Pnt(e.start, 1, True)
        #     + "  "
        #     + "end: "
        #     + print_gp_Pnt(e.end, 1, True)
        # )
        gui.display(ais_edge, False)
        # ais_piece = AIS_Shape(make_piece(e))
        # ais_piece.SetColor(getColor(255, 0, 0))
        # ais_piece.SetTransparency(0.5)
        # # print("start: " + printPnt(e.start, 1, True) + "  " + "end: " + printPnt(e.end, 1, True))
        # gui.display(ais_piece, False)
    # end for

    # for e in second_list:
    #     ais_sed = AIS_Shape(e.topo_edge)
    #     ais_sed.SetWidth(5)
    #     ais_sed.SetTransparency(0.9)
    #     ais_sed.SetColor(getColor(0, 255, 0))
    #     gui.display(ais_sed, False)
    # # end for

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
    global GUI
    GUI = gui
    test(gui)
    # 窗口置顶
    gui.raise_()
    app.exec()


GUI: MainWindow = None
# end def
if __name__ == "__main__":
    mainGUI()
# end main
