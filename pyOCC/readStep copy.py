import os

from loguru import logger
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.IFSelect import IFSelect_ItemsByEntity, IFSelect_RetDone, IFSelect_ReturnStatus
from OCC.Core.Quantity import Quantity_Color, Quantity_NameOfColor, Quantity_TOC_RGB
from OCC.Core.Standard import Standard_GUID
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.TDataStd import TDataStd_Name
from OCC.Core.TDF import TDF_Attribute, TDF_AttributeIterator, TDF_Label, TDF_LabelSequence
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.XCAFDoc import XCAFDoc_ColorTool, XCAFDoc_ColorType, XCAFDoc_DocumentTool


def getColor(r: int | tuple[int, int, int], g=0, b=0):
    if isinstance(r, tuple):
        r, g, b = r
    return Quantity_Color(r / float(255), g / float(255), b / float(255), Quantity_TOC_RGB)


# end def
def readStepPartShape(dir_path: str) -> TopoDS_Shape:
    """read the STEP file and returns a compound"""
    # 生成一个 step 模型类
    reader = STEPControl_Reader()
    # 加载一个文件并且返回一个状态枚举值
    status = reader.ReadFile(dir_path)

    # 如果正常执行且有模型
    if status == IFSelect_RetDone:  # check status
        fails_only = False
        # 如果存在无效或者不完整步骤实体，会显示错误信息
        reader.PrintCheckLoad(fails_only, IFSelect_ItemsByEntity)
        reader.PrintCheckTransfer(fails_only, IFSelect_ItemsByEntity)

        # 执行步骤文件转换
        ok = reader.TransferRoot(1)
        # # 返回生成形状的数量
        # _nbs = reader.NbShapes()
        # print(_nbs)
        # 返回转换后的形状
        aResShape = reader.Shape(1)
    else:
        print("模型加载失败")
        # sys.exit(0)
    return aResShape


# end def
def readStep(step_file):
    count, lvl = 0, 0
    if not os.path.isfile(step_file):
        raise Exception(f"文件不存在{step_file} not found.")

    output_shapes: dict[TopoDS_Shape, list[str, Quantity_Color]] = {}
    # 创建一个文档用于模型树构建
    doc = TDocStd_Document("doc")
    # 获取根节点
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())
    layer_tool = XCAFDoc_DocumentTool.LayerTool(doc.Main())
    material_tool = XCAFDoc_DocumentTool.MaterialTool(doc.Main())

    # STEP读取器
    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)
    step_reader.SetGDTMode(True)

    status = step_reader.ReadFile(step_file)
    match (status):
        case (IFSelect_ReturnStatus.IFSelect_RetDone):
            step_reader.Transfer(doc)
            logger.success("加载成功")
        case IFSelect_ReturnStatus.IFSelect_RetVoid:
            raise (f"模型为空")
        case IFSelect_ReturnStatus.IFSelect_RetError:
            raise (f"加载错误")
        case IFSelect_ReturnStatus.IFSelect_RetFail:
            raise (f"模型加载失败")
        case IFSelect_ReturnStatus.IFSelect_RetStop:
            raise (f"加载停止")
        case (_):
            raise (f"模型加载失败")
    # end match
    locations: list[TopLoc_Location] = []

    def _get_sub_shapes(label: TDF_Label, location: TopLoc_Location):
        """获取子节点形状

        Parameters
        ----------
        `label` : TDF_Label
            _description_
        `location` : TopLoc_Location
            _description_
        """
        nonlocal count, lvl
        count += 1
        str = f"     层级: {lvl}, 标签名: {label.GetLabelName()}"

        if shape_tool.IsAssembly(label):
            str += ", Assembly"
        if shape_tool.IsFree(label):
            str += ", Free"
        if shape_tool.IsShape(label):
            str += ", Shape"
        if shape_tool.IsCompound(label):
            str += ", Compound"
        if shape_tool.IsComponent(label):
            str += ", Component"
        if shape_tool.IsSimpleShape(label):
            str += ", SimpleShape"
        if shape_tool.IsReference(label):
            str += ", Reference"
        print(str)
        # users = TDF_LabelSequence()
        # users_count = shape_tool.GetUsers(label, users)
        # print("用户标签数:", users_count)

        label_subs_shapes = TDF_LabelSequence()
        shape_tool.GetSubShapes(label, label_subs_shapes)
        print("子形状数目   :", label_subs_shapes.Length())
        label_components = TDF_LabelSequence()
        shape_tool.GetComponents(label, label_components)
        print("组件数目  :", label_components.Length())
        # print()
        # name = label.GetLabelName()
        # print("标签名 :", name)
        # 如果是装配体
        if shape_tool.IsAssembly(label):
            l_c = TDF_LabelSequence()
            shape_tool.GetComponents(label, l_c)
            for i in range(l_c.Length()):
                label = l_c.Value(i + 1)
                if shape_tool.IsReference(label):
                    label_reference = TDF_Label()
                    shape_tool.GetReferredShape(label, label_reference)
                    location = shape_tool.GetLocation(label)

                    locations.append(location)
                    lvl += 1
                    _get_sub_shapes(label_reference, location)
                    lvl -= 1
                    locations.pop()
                # end if
            # end for
            if locations:
                print(
                    f"    装配体坐标：{int(locations[-1].Transformation().TranslationPart().X())}, {int(locations[0].Transformation().TranslationPart().Y())}, {int(locations[0].Transformation().TranslationPart().Z())}"
                )
        # 如果是单个形状
        elif shape_tool.IsSimpleShape(label):
            # print("\n########  simpleshape label :", label)
            shape = shape_tool.GetShape(label)
            if locations:
                print(
                    f"    坐标：{int(locations[-1].Transformation().TranslationPart().X())}, {int(locations[0].Transformation().TranslationPart().Y())}, {int(locations[0].Transformation().TranslationPart().Z())}"
                )

            location = TopLoc_Location()
            for l in locations:
                location = location.Multiplied(l)

            c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
            color_set = False
            if (
                color_tool.GetInstanceColor(shape, 0, c)
                or color_tool.GetInstanceColor(shape, 1, c)
                or color_tool.GetInstanceColor(shape, 2, c)
            ):
                color_tool.SetInstanceColor(shape, 0, c)
                color_tool.SetInstanceColor(shape, 1, c)
                color_tool.SetInstanceColor(shape, 2, c)
                color_set = True
            # end if
            # if not color_set:
            elif (
                XCAFDoc_ColorTool.GetColor(label, 0, c)
                or XCAFDoc_ColorTool.GetColor(label, 1, c)
                or XCAFDoc_ColorTool.GetColor(label, 2, c)
            ):
                color_tool.SetInstanceColor(shape, 0, c)
                color_tool.SetInstanceColor(shape, 1, c)
                color_tool.SetInstanceColor(shape, 2, c)
            # end if
            shape_disp = BRepBuilderAPI_Transform(shape, location.Transformation()).Shape()

            if shape_disp not in output_shapes:
                output_shapes[shape_disp] = [label.GetLabelName(), c]
            # 处理子形状
            for i in range(label_subs_shapes.Length()):
                lab_subs = label_subs_shapes.Value(i + 1)
                print("\n########  子形状标签 :", label.GetLableName())
                shape_sub = shape_tool.GetShape(lab_subs)

                c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                color_set = False
                if (
                    XCAFDoc_ColorTool.GetInstanceColor(shape_sub, 0, c)
                    or XCAFDoc_ColorTool.GetInstanceColor(shape_sub, 1, c)
                    or XCAFDoc_ColorTool.GetInstanceColor(shape_sub, 2, c)
                ):
                    color_tool.SetInstanceColor(shape_sub, 0, c)
                    color_tool.SetInstanceColor(shape_sub, 1, c)
                    color_tool.SetInstanceColor(shape_sub, 2, c)
                    color_set = True
                # end if
                if not color_set:
                    if (
                        XCAFDoc_ColorTool.GetColor(lab_subs, 0, c)
                        or XCAFDoc_ColorTool.GetColor(lab_subs, 1, c)
                        or XCAFDoc_ColorTool.GetColor(lab_subs, 2, c)
                    ):
                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)
                    # end if
                # end if
                shape_to_disp = BRepBuilderAPI_Transform(shape_sub, location.Transformation()).Shape()
                # position the subshape to display
                if shape_to_disp not in output_shapes:
                    output_shapes[shape_to_disp] = [lab_subs.GetLabelName(), c]

    # end def
    def _get_shapes():
        labels = TDF_LabelSequence()
        shape_tool.GetFreeShapes(labels)
        nonlocal count
        count += 1

        # print()
        # print("Number of shapes at root :", labels.Length())
        # print()
        logger.info(f"共有{labels.Length()}个根节点")
        for i in range(labels.Length()):
            root_item = labels.Value(i + 1)
            _get_sub_shapes(root_item, None)

    # end def
    _get_shapes()
    return output_shapes


# end def
if __name__ == "__main__":
    readStep(r"D:/ICO/RobotPlatform/input/test-read_assemble_within_colored.STEP")
    readStep(r"D:/ICO/RobotPlatform/input/test-read_assemble_includ_assemble.STEP")
    readStep(r"D:/ICO/RobotPlatform/input/测试1.STEP")
# end main
