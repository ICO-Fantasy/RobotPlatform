from dataclasses import dataclass

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
@dataclass
class MyEdge:
    shape: TopoDS_Shape | TopoDS_Edge
    length: float
    points: list[gp_Pnt]


# end class
def getEdgeData(topo_edge: TopoDS_Edge | TopoDS_Shape):
    brep_edge = BRepAdaptor_Curve(topo_edge)
    # 曲线类型
    type = brep_edge.GetType()
    # 直线参数 (直线长度)
    if type == GeomAbs_CurveType.GeomAbs_Line:
        start_param = brep_edge.FirstParameter()
        end_param = brep_edge.LastParameter()
        curve_length = end_param - start_param
        length = curve_length
    # 圆线段参数
    elif type == GeomAbs_CurveType.GeomAbs_Circle:
        circle = brep_edge.Circle()
        # 获取圆心坐标
        circle_center = circle.Location()
        # 获取圆半径
        circle_radius = circle.Radius()
        # 曲线长度
        length = GCPnts_AbscissaPoint.Length(brep_edge)
    # end if
    # edge_index = TopTools_IndexedMapOfShape()
    # topexp.MapShapes(sec_shape, TopAbs_ShapeEnum.TopAbs_EDGE, edge_index)
    a_point_explorer = TopExp_Explorer(topo_edge, TopAbs_ShapeEnum.TopAbs_VERTEX)
    points: list[gp_Pnt] = []
    while a_point_explorer.More():
        topo_point: TopoDS_Vertex = a_point_explorer.Current()  # 遍历得到每一个点
        a_point_explorer.Next()
        points.append(BRep_Tool.Pnt(topo_point))
    return MyEdge(shape=topo_edge, length=length, points=points)


# end def
def test(gui: MainWindow):
    """
    ========================================================================================
    TEST
    ========================================================================================
    """

    a_bending = read_step(r"test.STEP")

    bbox = Bnd_Box()
    brepbndlib.Add(a_bending, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin
    left_point = gp_Pnt(xmin, ymin, 0)
    right_point = gp_Pnt(xmax, ymax, 1)

    base_box = BRepPrimAPI_MakeBox(left_point, right_point).Shape()
    ais_base_box = AIS_Shape(base_box)
    gui.display(ais_base_box, False)

    # print 'slicing index:', z, 'sliced by process:', os.getpid()
    plane = gp_Pln(gp_Pnt(xmax / 2, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    face = BRepBuilderAPI_MakeFace(plane).Shape()

    # Computes Shape/Plane intersection
    section = BRepAlgoAPI_Section(a_bending, face)
    section.Build()
    if section.IsDone():
        sec_shape = section.Shape()
        ais_sec = AIS_Shape(sec_shape)
        gui.display(ais_sec, True)

    # edge_index = TopTools_IndexedMapOfShape()
    # topexp.MapShapes(sec_shape, TopAbs_ShapeEnum.TopAbs_EDGE, edge_index)
    a_edge_explorer = TopExp_Explorer(a_bending, TopAbs_ShapeEnum.TopAbs_FACE)
    theDir = gp_Dir(0, 1, 0)
    first_edges = []
    test_num = 0
    while a_edge_explorer.More():
        topo_edge = a_edge_explorer.Current()  # 遍历得到每一个边
        a_edge_explorer.Next()
        test_num = test_num + 1

        # edge_data = getEdgeData(topo_edge)
        # # print(edge_data.length)
        # # for p in edge_data.points:
        # #     print(f"{p.X()},{p.Y()},{p.Z()}")
        # a_dir = gp_Dir(gp_Vec(edge_data.points[0], edge_data.points[1]))
        # if theDir.IsParallel(a_dir, 1e-2):
        #     first_edges.append(topo_edge)
        #     ais_face = AIS_Shape(topo_edge)
        #     ais_face.SetColor(getColor(0, 255, 0))
        #     gui.display(ais_face, True)
    print(test_num)
    ais_face = AIS_Shape(a_bending)
    ais_face.SetColor(getColor(0, 0, 255))
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
