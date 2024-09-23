from loguru import logger

# OCC
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepTools import breptools
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.RWMesh import (
    RWMesh_CoordinateSystem_negZfwd_posYup,
    RWMesh_CoordinateSystem_posYfwd_posZup,
)
from OCC.Core.RWObj import RWObj_CafWriter
from OCC.Core.TColStd import TColStd_IndexedDataMapOfStringString
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.UnitsMethods import unitsmethods
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool


def write_obj(shape: TopoDS_Shape, file_name: str):
    # 构建 Doc
    doc = TDocStd_Document("")
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())

    # 构建网格形状
    breptools.Clean(shape)
    msh_algo = BRepMesh_IncrementalMesh(shape, True)
    msh_algo.Perform()

    shape_tool.AddShape(shape)

    # 元数据
    a_file_info = TColStd_IndexedDataMapOfStringString()

    rwobj_writer = RWObj_CafWriter(file_name)

    # apply a scale factor of 0.001 to mimic conversion from m to mm
    # 单位转换从 m 到 mm
    csc = rwobj_writer.ChangeCoordinateSystemConverter()
    system_unit_factor = unitsmethods.GetCasCadeLengthUnit() * 0.001
    csc.SetInputLengthUnit(system_unit_factor)
    csc.SetOutputLengthUnit(system_unit_factor)
    csc.SetInputCoordinateSystem(RWMesh_CoordinateSystem_posYfwd_posZup)
    csc.SetOutputCoordinateSystem(RWMesh_CoordinateSystem_negZfwd_posYup)

    rwobj_writer.SetCoordinateSystemConverter(csc)

    rwobj_writer.Perform(doc, a_file_info, Message_ProgressRange())
    logger.success(f"导出成功：{file_name}")


if __name__ == "__main__":

    print("done")
# end main
