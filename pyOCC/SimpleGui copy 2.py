import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from OCC.Core.AIS import AIS_Trihedron, AIS_ViewCube
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.Geom import Geom_Axis2Placement
from OCC.Core.gp import *
from OCC.Core.Prs3d import *
from OCC.Core.Quantity import *
from OCC.Display.OCCViewer import Viewer3d
from OCC.Display.SimpleGui import init_display

from . import createTrihedron


def getColor(r, g, b):
    return Quantity_Color(r / float(255), g / float(255), b / float(255), Quantity_TOC_RGB)


def my_viewer_decorator(init_display_func):
    def wrapped_init_display(*args, **kwargs):
        display, start_display, add_menu, add_function_to_menu = init_display_func(*args, **kwargs)

        class MyViewer3d(Viewer3d):
            XAxis = Prs3d_DatumParts.Prs3d_DatumParts_XAxis
            YAxis = Prs3d_DatumParts.Prs3d_DatumParts_YAxis
            ZAxis = Prs3d_DatumParts.Prs3d_DatumParts_ZAxis
            Xcolor = getColor(0, 255, 0)
            Ycolor = getColor(0, 0, 255)
            Zcolor = getColor(255, 0, 0)

            def __init__(self, display: Viewer3d, display_triedron=False, display_view_cube=True, display_origin_trihedron=True):
                super().__init__()
                self.display = display
                if display_triedron:
                    self.displayTriedron()
                if display_view_cube:
                    self.displayViewCube()
                if display_origin_trihedron:
                    self.displayOriginTrihedron()

            def displayTriedron(self):
                self.display.display_triedron()

            def displayViewCube(self):
                a_view_cube = AIS_ViewCube()
                aDrawer = a_view_cube.Attributes()
                aDrawer.SetDatumAspect(Prs3d_DatumAspect())
                aDatumAsp = aDrawer.DatumAspect()
                aDatumAsp.TextAspect(self.XAxis).SetColor(self.Xcolor)
                aDatumAsp.TextAspect(self.YAxis).SetColor(self.Ycolor)
                aDatumAsp.TextAspect(self.ZAxis).SetColor(self.Zcolor)
                self.display.Context.Display(a_view_cube, True)

            def displayOriginTrihedron(self):
                a_origin_trihedron = createTrihedron()
                self.display.Context.Display(a_origin_trihedron, True)

        my_viewer = MyViewer3d(display, *args, **kwargs)
        return display, start_display, add_menu, add_function_to_menu

    return wrapped_init_display


@my_viewer_decorator
def initDisplay(size=(1920, 980), display_triedron=False, display_view_cube=True, display_origin_trihedron=True):
    return init_display(size=size, display_triedron=display_triedron)


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = initDisplay()
    start_display()
