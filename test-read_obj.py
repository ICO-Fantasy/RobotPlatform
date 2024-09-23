import time

from OCC.Core.AIS import AIS_Shape
from OCC.Core.gp import gp_Trsf, gp_Vec
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TDataStd import TDataStd_Name
from OCC.Core.TDF import TDF_Attribute, TDF_Label, TDF_LabelSequence
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TopoDS import TopoDS_Shape

# from OCC.Core.UnitsMethods import unitsmethods
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCC.Core.XCAFPrs import XCAFPrs_AISObject
from OCC.Display.SimpleGui import init_display


def ReadObjWithColor(filename):
    obj_reader = RWObj_CafReader()
    astr = TCollection_ExtendedString("a_doc")
    a_doc = TDocStd_Document(astr)
    # a_doc = TDocStd_Document("a_doc")
    obj_reader.SetSinglePrecision(True)
    # obj_reader.SetSystemLengthUnit(unitsmethods.GetCasCadeLengthUnit() * 0.001)
    obj_reader.SetSystemLengthUnit(0.001)
    obj_reader.SetSystemCoordinateSystem(RWMesh_CoordinateSystem_Zup)
    obj_reader.SetFileLengthUnit(0.001)
    obj_reader.SetFileCoordinateSystem(RWMesh_CoordinateSystem_Zup)
    obj_reader.SetDocument(a_doc)

    status = obj_reader.Perform(TCollection_AsciiString(filename), Message_ProgressRange())
    # status = obj_reader.Perform(filename, Message_ProgressRange())
    if not status:
        print(f"读取 OBJ 文件失败。返回状态：{status}")
        return None
    root_label = a_doc.Main()
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(root_label)
    # print(f"{shape_tool.IsSimpleShape(root_label)}")
    # print(f"{shape_tool.IsAssembly(root_label)}")
    # print(f"{shape_tool.IsComponent(root_label)}")
    # print(f"{shape_tool.IsTopLevel(root_label)}")
    print(f"是自由形状：{shape_tool.IsFree(root_label)}")
    # print(f"{shape_tool.IsShape(root_label)}")
    # print(f"{shape_tool.IsExternRef(root_label)}")
    # print(f"是一个形状：{shape_tool.IsSimpleShape(root_label)}")
    print(f"是否有子标签：{root_label.HasChild()}")
    label_seq = TDF_LabelSequence()
    shape_tool.GetFreeShapes(label_seq)
    # aName = TDataStd_Name()
    # eq_seq_label = label_seq.Value(1)
    first_seq_label = label_seq.First()
    # print(f"是第一个标签：{eq_seq_label.IsEqual(first_seq_label)}, 共{label_seq.Size()}个")
    ais_obj = XCAFPrs_AISObject(first_seq_label)
    # if first_seq_label.FindAttribute(aName.GetID(), aName):
    # ais_obj.SetShape(shape_tool.GetShape(eq_seq_label))
    a_shape = shape_tool.GetShape(first_seq_label)
    return ais_obj, a_shape


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()
    an_ais, a_shape = ReadObjWithColor("blade_mesh.obj")
    # an_ais, a_shape = ReadObjWithColor("cube-10-10-10.obj")
    atrsf = gp_Trsf()
    atrsf.SetTranslation(gp_Vec(50, 0, 0))
    an_ais.SetLocalTransformation(atrsf)
    display.Context.Display(an_ais, True)
    display.Context.Display(AIS_Shape(a_shape), True)
    start_display()
    print("done")
# end main
