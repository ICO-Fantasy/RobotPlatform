from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Quantity import Quantity_Color
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.TDF import TDF_Label, TDF_LabelSequence
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.XCAFDoc import XCAFDoc_ColorTool, XCAFDoc_ColorType, XCAFDoc_DocumentTool

from .getColor import getColor


def read_step_file_with_names_colors(
    filename,
) -> dict[TopoDS_Shape, list[TopoDS_Shape | Quantity_Color]]:
    """Returns list of tuples (topods_shape, label, color)
    Use OCAF.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} not found.")
    # the list:
    output_shapes = {}

    # create an handle to a document
    # doc_str = TCollection_ExtendedString("doc")
    doc = TDocStd_Document("doc")

    # Get root assembly
    # shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
    # color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())
    color_tool = XCAFDoc_DocumentTool.ColorTool(doc.Main())

    # layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())
    # mat_tool = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)
    step_reader.SetGDTMode(True)

    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)

    locs = []

    def _get_sub_shapes(label, loc):
        l_subss = TDF_LabelSequence()
        shape_tool.GetSubShapes(label, l_subss)
        l_comps = TDF_LabelSequence()
        shape_tool.GetComponents(label, l_comps)
        name = label.GetLabelName()
        # print("Name :", name)

        if shape_tool.IsAssembly(label):
            l_c = TDF_LabelSequence()
            shape_tool.GetComponents(label, l_c)
            for i in range(l_c.Length()):
                label = l_c.Value(i + 1)
                if shape_tool.IsReference(label):
                    label_reference = TDF_Label()
                    shape_tool.GetReferredShape(label, label_reference)
                    loc = shape_tool.GetLocation(label)

                    locs.append(loc)
                    _get_sub_shapes(label_reference, loc)
                    locs.pop()

        elif shape_tool.IsSimpleShape(label):
            shape = shape_tool.GetShape(label)

            loc = TopLoc_Location()
            for l in locs:
                loc = loc.Multiplied(l)
            c = getColor(125, 125, 125)  # default color
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
                n = c.Name(c.Red(), c.Green(), c.Blue())
                # print(
                #     "    instance color Name & RGB: ",
                #     c,
                #     n,
                #     c.Red(),
                #     c.Green(),
                #     c.Blue(),
                # )

            if not color_set:
                color_tool.GetInstanceColor(shape, 0, c)
                # color_tool.GetColor(label, XCAFDoc_ColorType.XCAFDoc_ColorGen, c)
                # color_tool.GetColor(L=label, type=0, color=c)
                if (
                    XCAFDoc_ColorTool.GetColor(label, 0, c)
                    or XCAFDoc_ColorTool.GetColor(label, 1, c)
                    or XCAFDoc_ColorTool.GetColor(label, 2, c)
                ):
                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)

                    # n = c.Name(c.Red(), c.Green(), c.Blue())
                    # print(
                    #     "    shape color Name & RGB: ",
                    #     c,
                    #     n,
                    #     c.Red(),
                    #     c.Green(),
                    #     c.Blue(),
                    # )

            shape_disp = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()
            if not shape_disp in output_shapes:
                output_shapes[shape_disp] = [label.GetLabelName(), c]
            for i in range(l_subss.Length()):
                lab_subs = l_subss.Value(i + 1)
                shape_sub = shape_tool.GetShape(lab_subs)

                c = getColor(125, 125, 125)  # default color
                color_set = False
                if (
                    color_tool.GetInstanceColor(shape_sub, 0, c)
                    or color_tool.GetInstanceColor(shape_sub, 1, c)
                    or color_tool.GetInstanceColor(shape_sub, 2, c)
                ):
                    color_tool.SetInstanceColor(shape_sub, 0, c)
                    color_tool.SetInstanceColor(shape_sub, 1, c)
                    color_tool.SetInstanceColor(shape_sub, 2, c)
                    color_set = True
                    # n = c.Name(c.Red(), c.Green(), c.Blue())
                    # print(
                    #     "    instance color Name & RGB: ",
                    #     c,
                    #     n,
                    #     c.Red(),
                    #     c.Green(),
                    #     c.Blue(),
                    # )

                if not color_set:
                    if (
                        XCAFDoc_ColorTool.GetColor(label, 0, c)
                        or XCAFDoc_ColorTool.GetColor(label, 1, c)
                        or XCAFDoc_ColorTool.GetColor(label, 2, c)
                    ):
                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)

                        # n = c.Name(c.Red(), c.Green(), c.Blue())
                        # print(
                        #     "    shape color Name & RGB: ",
                        #     c,
                        #     n,
                        #     c.Red(),
                        #     c.Green(),
                        #     c.Blue(),
                        # )
                shape_to_disp = BRepBuilderAPI_Transform(shape_sub, loc.Transformation()).Shape()
                # position the subshape to display
                if not shape_to_disp in output_shapes:
                    output_shapes[shape_to_disp] = [lab_subs.GetLabelName(), c]

    def _get_shapes():
        labels = TDF_LabelSequence()
        shape_tool.GetFreeShapes(labels)

        # print()
        # print("Number of shapes at root :", labels.Length())
        # print()
        for i in range(labels.Length()):
            root_item = labels.Value(i + 1)
            _get_sub_shapes(root_item, None)

    _get_shapes()
    return output_shapes


def readStepWithColor(file_path: str):
    a_dict = read_step_file_with_names_colors(file_path)
    keys = list(a_dict.keys())
    shape: TopoDS_Shape = keys[0]
    quantity_color: Quantity_Color = a_dict[shape][1]
    return shape, quantity_color


if __name__ == "__main__":
    shape, color = readStepWithColor(r"D:\ICO\PipeBending\mods\pipbendmachine\模具底座 Y.STEP")
    print(shape)
    print(color)
# end main
