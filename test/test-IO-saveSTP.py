from context import *

step_file = Path("test-step.stp")
target_path = Path(".").absolute().resolve().joinpath("output").joinpath(step_file.name)

# 创建几何对象（这里以一个简单的盒子为例）
box = BRepPrimAPI_MakeBox(10, 10, 10).Shape()

# initialize the STEP exporter
step_writer = STEPControl_Writer()
dd = step_writer.WS().TransferWriter().FinderProcess()
print(dd)

Interface_Static.SetCVal("write.step.schema", "AP203")

# transfer shapes and write file
step_writer.Transfer(box, STEPControl_AsIs)
status = step_writer.Write(str(target_path))

if status != IFSelect_RetDone:
    raise AssertionError("load failed")
print(f"{step_file.name} saved")
