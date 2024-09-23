import math
from functools import partial

from OCC.Core.AIS import AIS_MultipleConnectedInteractive, AIS_Shape
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder
from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from OCC.Core.Quantity import Quantity_Color

from pyOCC import COLOR, LocalCONFIG


class AIS_Shape_Tri(AIS_MultipleConnectedInteractive):
    def __init__(self, ais_shape: AIS_Shape | None = None, arrow_length=100):
        super().__init__()
        if not ais_shape:
            self.ais_shape = None
        else:
            self.ais_shape = ais_shape
            self.Connect(ais_shape)
            self.calculate_arrow_length()
        if arrow_length != 100:
            self.arrow_length = arrow_length
        x = self.make_arrow(gp_Dir(1, 0, 0))
        y = self.make_arrow(gp_Dir(0, 1, 0))
        z = self.make_arrow(gp_Dir(0, 0, 1))
        [(self.Connect(element), _SetColor(LocalCONFIG.X_AXIS_COLOR, element)) for element in x]
        [(self.Connect(element), _SetColor(LocalCONFIG.Y_AXIS_COLOR, element)) for element in y]
        [(self.Connect(element), _SetColor(LocalCONFIG.Z_AXIS_COLOR, element)) for element in z]

    # end alternate constructor
    def calculate_arrow_length(self):
        # 计算包围盒
        bbox = Bnd_Box()
        brepbndlib.Add(self.ais_shape.Shape(), bbox)
        x_min, y_min, z_min, x_max, y_max, z_max = bbox.Get()
        dx = x_max - x_min
        dy = y_max - y_min
        dz = z_max - z_min
        self.arrow_length = max([dx, dy, dz]) * 1.3
        # end def

    def make_arrow(self, arrow_dir: gp_Dir):
        real_dir = arrow_dir
        if self.ais_shape:
            real_dir = arrow_dir.Transformed(self.ais_shape.LocalTransformation())
        arrow_angle = 18
        start_point = gp_Pnt()
        if self.ais_shape:
            start_point.Transformed(self.ais_shape.LocalTransformation())
        cone_scale = 2
        arrow_length = self.arrow_length
        arrow_radius = arrow_length / 60
        bottom_radius = arrow_radius * cone_scale
        arrow_high = bottom_radius / math.tan(math.radians(arrow_angle))
        cone_start = start_point.Translated(gp_Vec(real_dir).Scaled(arrow_length - arrow_high))

        def _makeCone():
            """创建锥体并将其存储为 self.cone"""
            axis = gp_Ax2(cone_start, real_dir)
            cone = BRepPrimAPI_MakeCone(axis, bottom_radius, 0, arrow_high).Shape()
            return AIS_Shape(cone)

        def _makeCylinder():
            """创建圆柱体并将其存储为 self.cylinder"""
            axis = gp_Ax2(start_point, real_dir)
            cylinder = BRepPrimAPI_MakeCylinder(
                axis, arrow_radius, arrow_length - arrow_high
            ).Shape()
            return AIS_Shape(cylinder)

        cone, cylinder = _makeCone(), _makeCylinder()
        return cone, cylinder

    # end def
    def SetColor(self, color: Quantity_Color):
        self.ais_shape.SetColor(color)

    # end def
    def SetTransparency(self, value: float | None = 0.6):
        self.ais_shape.SetTransparency(value)

    # end def


# end class


def _SetColor(theColor: Quantity_Color, input_ais: AIS_Shape):
    """设置锥体和圆柱体的颜色"""
    input_ais.SetColor(theColor)


# end def


if __name__ == "__main__":
    pass
    # display, start_display, add_menu, add_function_to_menu = init_display(size=(1920, 980), display_triedron=True)

    # a_ais = AIS_Shape_Tri(gp_Pnt(*(0, 0, 0)), gp_Dir(*(1, 0, 0)))
    # display.Context.Display(a_ais, True)
    # display.FitAll()
    # start_display()
# end main
