import math
import random
import time

from context import *

LINEAR_TOLERANCE_LIST = [
    # 1e-4,
    # 1e-3,
    # 5e-3,
    # 1e-2,
    # 5e-2,
    # 1e-1,
    # 5e-1,
    5e-2,
]
LINEAR_TOLERANCE = 0.2
# LINEAR_TOLERANCE = 1e-6


def get_bnd(shape: TopoDS_Shape):
    bbox = Bnd_Box()
    brepbndlib.Add(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin
    return xmin, ymin, zmin, xmax, ymax, zmax


# end def


class Edge:
    def __init__(self, edge: TopoDS_Edge):
        self.topo_edge: TopoDS_Edge = edge
        self.dir = True
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


def count_shape_types(shape: TopoDS_Shape):
    shape_type_count = {"VERTEX": 0, "EDGE": 0, "FACE": 0, "SHELL": 0, "SOLID": 0, "SHAPE": 0}

    # 统计 VERTEX
    explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
    while explorer.More():
        shape_type_count["VERTEX"] += 1
        explorer.Next()

    # 统计 EDGE
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while explorer.More():
        shape_type_count["EDGE"] += 1
        explorer.Next()

    # 统计 FACE
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        shape_type_count["FACE"] += 1
        explorer.Next()

    # 统计 SHELL
    explorer = TopExp_Explorer(shape, TopAbs_SHELL)
    while explorer.More():
        shape_type_count["SHELL"] += 1
        explorer.Next()

    # 统计 SOLID
    explorer = TopExp_Explorer(shape, TopAbs_SOLID)
    while explorer.More():
        shape_type_count["SOLID"] += 1
        explorer.Next()

    # 统计 SHAPE
    explorer = TopExp_Explorer(shape, TopAbs_SHAPE)
    while explorer.More():
        shape_type_count["SHAPE"] += 1
        explorer.Next()

    # 打印每种类型的数量
    for shape_type, count in shape_type_count.items():
        print(f"{shape_type}: {count}")


# end def
def getEdges(shape: TopoDS_Shape):
    count_shape_types(shape)
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
    start_list = []
    end_list = []

    # for e in edge_list:
    #     start_list.append(e.start.Distance(edge_dict["end"]))
    #     end_list.append(e.end.Distance(edge_dict["start"]))
    # print(f"start:{min(start_list)} end: {min(end_list)}")
    for e in edge_list:
        if e.start.Distance(edge_dict["end"]) < LINEAR_TOLERANCE and e.dir == edge_dict["dir"]:
            edge_dict["end"] = e.end
            edge_dict["edge"].append(e)
            edge_list.remove(e)
            return True
        if e.end.Distance(edge_dict["start"]) < LINEAR_TOLERANCE and e.dir == edge_dict["dir"]:
            edge_dict["start"] = e.start
            edge_dict["edge"].insert(0, e)
            edge_list.remove(e)
            return True
    return False


# end def
def get_ring(edges: list[Edge]):
    rings = []
    continue_flag = True
    while edges:
        if continue_flag:
            an_edge = edges.pop(0)
            start = an_edge.start
            end = an_edge.end
            a_ring = [an_edge]
            rings.append(a_ring)
            continue_flag = False
        for e in edges:
            if start.IsEqual(e.start, LINEAR_TOLERANCE):
                # if start.Distance(e.start) < LINEAR_TOLERANCE:
                a_ring.append(e)
                end = e.end
                edges.remove(e)
                break
            elif start.IsEqual(e.end, LINEAR_TOLERANCE):
                # elif start.Distance(e.end) < LINEAR_TOLERANCE:
                a_ring.append(e)
                start = e.start
                edges.remove(e)
                break
            elif end.IsEqual(e.end, LINEAR_TOLERANCE):
                # elif end.Distance(e.end) < LINEAR_TOLERANCE:
                a_ring.append(e)
                end = e.start
                edges.remove(e)
                break
            elif end.IsEqual(e.start, LINEAR_TOLERANCE):
                # elif end.Distance(e.start) < LINEAR_TOLERANCE:
                a_ring.append(e)
                end = e.end
                edges.remove(e)
                break
            if start.Distance(e.start) < 5.0:
                print(f"{start.Distance(e.start):.4f}")
            if start.Distance(e.end) < 5.0:
                print(f"{start.Distance(e.end):.4f}")
            if end.Distance(e.start) < 5.0:
                print(f"{end.Distance(e.start):.4f}")
            if end.Distance(e.end) < 5.0:
                print(f"{end.Distance(e.end):.4f}")
        else:
            continue_flag = True
    return rings


# end def

# # * 移除竖直的线
# new_edge: list[Edge] = []
# z_dir = gp_Vec(0, 0, 1)
# for e in edges:
#     if gp_Vec(e.start, e.end).IsParallel(z_dir, 0.1):
#         continue
#     else:
#         new_edge.append(e)
# # end for


def get_edges(gui: MainWindow, cross_shape: TopoDS_Shape):
    #! 获取截面线
    edges: list[Edge] = getEdges(cross_shape)
    if not edges:
        return None
    rings = get_ring(edges)
    for ring in rings:
        get_wire(gui, ring)


# end def


def get_wire(gui: MainWindow, edges: list[Edge]):
    #! 线排序，并获得按顺序的起点
    wire_maker = BRepBuilderAPI_MakeWire()
    container = TopTools_ListOfShape()
    for e in edges:
        container.Append(e.topo_edge)
    # end for
    wire_maker.Add(container)
    if not wire_maker.IsDone():
        return
    wire_explorer = BRepTools_WireExplorer(wire_maker.Wire())
    ordered_edges: list[Edge] = []
    debug_num = 0

    while True:
        e = random.choice(edges)
        base_dir = gp_Vec2d(e.start_2d, e.end_2d)
        if base_dir.Magnitude() != 0.0:
            break
    # end for
    while wire_explorer.More():
        a_edge = Edge(wire_explorer.Current())
        # 起点排序
        current_point = BRep_Tool.Pnt(wire_explorer.CurrentVertex())
        if a_edge.start.Distance(current_point) > a_edge.end.Distance(current_point):
            a_edge.start, a_edge.end = a_edge.end, a_edge.start
        # 决定方向
        if gp_Vec2d(a_edge.start_2d, a_edge.end_2d).Magnitude() != 0.0:
            if gp_Vec2d(a_edge.start_2d, a_edge.end_2d).IsOpposite(base_dir, 1e-2):
                a_edge.dir = False
            else:
                a_edge.dir = True
        ordered_edges.append(a_edge)
        wire_explorer.Next()
    # end while

    # count dir
    dir_true_count = 0
    dir_false_count = 0
    for ee in ordered_edges:
        if ee.dir:
            dir_true_count += 1
        else:
            dir_false_count += 1

    print(f"true: {dir_true_count}, false: {dir_false_count}")
    # if dir_true_count > 2 or dir_false_count > 2:
    #     if abs(dir_true_count - dir_false_count) < 3:
    #         break
    # if debug_num > 4:
    #     break
    # debug_num += 1
    # # end while

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

    first_dict = {}

    #! 找到其中一条边
    finish = 2
    while finish:
        if not first_dict:
            first_edge = random.choice(ordered_edges)

            first_dict["start"] = first_edge.start
            first_dict["end"] = first_edge.end
            first_dict["edge"] = [first_edge]
            first_dict["dir"] = first_edge.dir

            ais_vertex = AIS_Shape(BRepPrimAPI_MakeSphere(first_edge.start, 0.5).Shape())
            ais_vertex.SetColor(COLOR.OCC_RED)
            ais_vertex.SetTransparency(0.5)
            gui.display(ais_vertex, True)
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
        ais_edge.SetColor(COLOR.OCC_RED)
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

    for e in second_list:
        ais_sed = AIS_Shape(e.topo_edge)
        ais_sed.SetWidth(5)
        ais_sed.SetTransparency(0.9)
        ais_sed.SetColor(COLOR.OCC_GREEN)
        gui.display(ais_sed, False)
    # end for


# end def


def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """
    gui.canvas.display_graduated_trihedron()
    gui.canvas.viewer3d.View_Right()

    # input_point = gp_Pnt(1000, 0, 0)
    # input_dir = gp_Dir(1, 0, 0)
    # autocorrect:false
    #! 读取工件
    # input_workpiece_shape = read_step(r"D:\Projects\FANUC激光切割机器人\简易夹具\无厚度工件.stp")
    # input_workpiece_shape = read_step(r".\laser-test1-Small-01.stp")
    # input_workpiece_shape = read_step(
    #     r"D:\ICO\CSharpOCCToolKit\TestWPF\bin\Debug\net6.0-windows10.0.17763.0\mods\test1.stp"
    # )
    # input_workpiece_shape = read_step(
    #     r"D:\ICO\CSharpOCCToolKit\TestWPF\bin\Debug\net6.0-windows10.0.17763.0\mods\test2.stp"
    # )
    input_workpiece_shape = read_step(
        r"D:\ICO\CSharpOCCToolKit\TestWPF\bin\Debug\net6.0-windows10.0.17763.0\mods\test5.stp"
    )
    # input_workpiece_shape = read_step(
    #     r"D:\ICO\CSharpOCCToolKit\TestWPF\bin\Debug\net6.0-windows10.0.17763.0\mods\test4.stp"
    # )
    # input_workpiece_shape = read_step(
    #     r"D:\ICO\CSharpOCCToolKit\TestWPF\bin\Debug\net6.0-windows10.0.17763.0\mods\mytest.stp"
    # )
    # autocorrect:true
    ais_box_shape = AIS_Shape(input_workpiece_shape)
    ais_box_shape.SetTransparency(0.9)
    ais_box_shape.SetColor(COLOR.OCC_GRAY)
    gui.display(ais_box_shape, False)

    xmin, ymin, zmin, xmax, ymax, zmax = get_bnd(input_workpiece_shape)

    base_plate = BRepPrimAPI_MakeBox(
        gp_Pnt(xmin, ymin, zmin - 11), gp_Pnt(xmax, ymax, zmin - 10)
    ).Shape()
    ais_box_shape = AIS_Shape(base_plate)
    ais_box_shape.SetTransparency(0.9)
    ais_box_shape.SetColor(COLOR(12, 125, 0)())
    gui.display(ais_box_shape, False)

    init_x = 20
    init_y = 20
    # init_x = (xmax - xmin) * 0.1
    # init_y = (ymax - ymin) * 0.1

    x_num = 3
    y_num = 3
    x_point_list = []
    y_point_list = []
    for i in range(x_num):
        x_point_list.append(
            gp_Pnt(init_x + xmin + i * (xmax - xmin - init_x * 2) / (x_num - 1), 0, 0)
        )
        print(f"x: {init_x + xmin + i * (xmax - xmin - init_x * 2) / (x_num - 1)}")
    for i in range(y_num):
        y_point_list.append(
            gp_Pnt(0, init_y + ymin + i * (ymax - ymin - init_y * 2) / (y_num - 1), 0)
        )
        print(f"y: {init_y + ymin + i * (ymax - ymin - init_y * 2) / (y_num - 1)}")
    x_dir = gp_Dir(1, 0, 0)
    y_dir = gp_Dir(0, 1, 0)

    # #! debug
    # x_point_list = [gp_Pnt(55.0, 1086.60, 0)]
    # y_point_list = []
    for xp in x_point_list:
        #! 创建截面并切割
        cross_plane = BRepBuilderAPI_MakeFace(gp_Pln(xp, x_dir)).Face()
        cross = BRepAlgoAPI_Section(input_workpiece_shape, cross_plane)
        cross.Approximation(True)

        # ais_cross = AIS_Shape(cross_shape)
        # gui.display(ais_cross, False)

        get_edges(gui, cross.Shape())

    # end for
    for yp in y_point_list:
        #! 创建截面并切割
        cross_plane = BRepBuilderAPI_MakeFace(gp_Pln(yp, y_dir)).Face()
        cross = BRepAlgoAPI_Section(input_workpiece_shape, cross_plane)
        cross.Approximation(True)
        # ais_cross = AIS_Shape(cross_shape)
        # gui.display(ais_cross, False)

        get_edges(gui, cross.Shape())
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
