# 创建几何对象（这里以一个简单的盒子为例）
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepTools import breptools
from OCC.Core.STEPControl import STEPControl_AsIs

box = BRepPrimAPI_MakeBox(10, 10, 10).Shape()

# 创建 BRepTools_Save 对象
brep_saver = breptools

# 设置保存模式为 STEPControl_AsIs（这样保存为 BREP 格式）
brep_saver.Write(box, "test-box.brep")
