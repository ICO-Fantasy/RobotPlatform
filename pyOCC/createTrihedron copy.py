import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from OCC.Core.AIS import AIS_InteractiveObject, AIS_MultipleConnectedInteractive, AIS_Shape, AIS_Trihedron, AIS_ViewCube
from OCC.Core.Geom import Geom_Axis2Placement
from OCC.Core.gp import *
from OCC.Core.Prs3d import *
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Display.OCCViewer import Viewer3d

from pyOCC import getColor


def bindTrihedron(ais_shape: AIS_Shape):
    ais_shape_trihedron = AIS_MultipleConnectedInteractive()
    ais_trihedron = createTrihedron(ais_shape)
    ais_shape_trihedron.AddChild(ais_shape)
    ais_shape_trihedron.AddChild(ais_trihedron)
    return ais_trihedron, ais_shape_trihedron


def createTrihedron(ais_shape: AIS_Shape):
    topo_location = ais_shape.Shape().Location()
    return __newTrihedron(topo_location)


def __newTrihedron(topo_location: TopLoc_Location):
    # 在topo_location创建一个坐标轴
    a_trsf = topo_location.Transformation()
    translation_part = a_trsf.TranslationPart()
    rotation_part = a_trsf.VectorialPart()
    origin = gp_Pnt(translation_part.X(), translation_part.Y(), translation_part.Z())
    direction = gp_Dir(rotation_part.Column(3))
    a_ax2 = gp_Ax2(origin, direction)
    a_geom = Geom_Axis2Placement(a_ax2)
    a_trihedron = AIS_Trihedron(a_geom)
    # a_trihedron.SetDatumDisplayMode(Prs3d_DM_WireFrame)
    a_trihedron.SetDrawArrows(True)
    a_trihedron.SetColor(getColor(0, 0, 255))
    a_trihedron.SetSize(10)
    a_trihedron.Attributes().DatumAspect().LineAspect(Prs3d_DP_XAxis).SetWidth(2.5)
    a_trihedron.Attributes().DatumAspect().LineAspect(Prs3d_DP_YAxis).SetWidth(2.5)
    a_trihedron.Attributes().DatumAspect().LineAspect(Prs3d_DP_ZAxis).SetWidth(2.5)
    a_trihedron.SetDatumPartColor(Prs3d_DatumParts.Prs3d_DatumParts_XAxis, getColor(0, 0, 255))
    a_trihedron.SetDatumPartColor(Prs3d_DatumParts.Prs3d_DatumParts_YAxis, getColor(0, 255, 0))
    a_trihedron.SetDatumPartColor(Prs3d_DatumParts.Prs3d_DatumParts_ZAxis, getColor(255, 0, 0))
    a_trihedron.SetArrowColor(Prs3d_DatumParts.Prs3d_DatumParts_XAxis, getColor(0, 0, 255))
    a_trihedron.SetArrowColor(Prs3d_DatumParts.Prs3d_DatumParts_YAxis, getColor(0, 255, 0))
    a_trihedron.SetArrowColor(Prs3d_DatumParts.Prs3d_DatumParts_ZAxis, getColor(255, 0, 0))
    a_trihedron.SetTextColor(Prs3d_DatumParts.Prs3d_DatumParts_XAxis, getColor(0, 0, 255))
    a_trihedron.SetTextColor(Prs3d_DatumParts.Prs3d_DatumParts_YAxis, getColor(0, 255, 0))
    a_trihedron.SetTextColor(Prs3d_DatumParts.Prs3d_DatumParts_ZAxis, getColor(255, 0, 0))
    return a_trihedron
