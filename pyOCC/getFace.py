from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepGProp import BRepGProp_Face
from OCC.Core.gp import gp_Vec
from OCC.Core.TopoDS import TopoDS_Face, TopoDS_Shape


def getFaceNormal(aface: TopoDS_Face | TopoDS_Shape):
    brepadp_face = BRepAdaptor_Surface(aface)  # type: ignore
    center_u = brepadp_face.FirstUParameter() + (brepadp_face.LastUParameter() - brepadp_face.FirstUParameter()) / 2
    center_v = brepadp_face.FirstVParameter() + (brepadp_face.LastVParameter() - brepadp_face.FirstVParameter()) / 2
    center_point = brepadp_face.Value(center_u, center_v)
    face_normal = gp_Vec()
    brep_face = BRepGProp_Face(aface)  # type: ignore
    brep_face.Normal(center_u, center_v, center_point, face_normal)  # face1的法线
    return face_normal


# end def
def getFaceCenter(aface: TopoDS_Face | TopoDS_Shape):
    brepadp_face = BRepAdaptor_Surface(aface)  # type: ignore
    center_u = brepadp_face.FirstUParameter() + (brepadp_face.LastUParameter() - brepadp_face.FirstUParameter()) / 2
    center_v = brepadp_face.FirstVParameter() + (brepadp_face.LastVParameter() - brepadp_face.FirstVParameter()) / 2
    center_point = brepadp_face.Value(center_u, center_v)
    return center_point


# end def
